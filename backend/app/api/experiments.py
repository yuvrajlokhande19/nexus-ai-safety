from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from ..models import ExperimentConfig, PersonaProfile, ResourceShare
from ..services.experiment_controller import experiment_controller
from ..core.ocean_traits import PersonaGenerator, Gender

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


class CreateExperimentRequest(BaseModel):
    name: str
    description: str
    topic: str
    persona_count: int = 5
    local_persona_count: int = 1
    rounds: int = 20
    initial_resources: List[Dict[str, str]] = []


class ResourceShareRequest(BaseModel):
    url: str
    title: str
    description: str
    shared_by: str
    tags: List[str] = []


@router.post("")
async def create_experiment(request: CreateExperimentRequest):
    """Create a new experiment with auto-generated personas"""
    personas = PersonaGenerator.create_balanced_group(
        request.persona_count, 
        request.local_persona_count
    )
    
    persona_profiles = [PersonaProfile(**p) for p in personas]
    
    config = ExperimentConfig(
        name=request.name,
        description=request.description,
        personas=persona_profiles,
        topic=request.topic,
        initial_resources=request.initial_resources,
        rounds=request.rounds
    )
    
    state = experiment_controller.create_experiment(config)
    return {"experiment_id": state.config.id, "status": "created"}


@router.post("/from-yaml")
async def create_experiment_from_yaml(yaml_path: str):
    """Create experiment from YAML config file"""
    try:
        state = experiment_controller.create_experiment_from_yaml(yaml_path)
        return {"experiment_id": state.config.id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_experiments():
    """List all experiments"""
    return experiment_controller.list_experiments()


@router.get("/{experiment_id}")
async def get_experiment(experiment_id: str):
    """Get experiment details"""
    state = experiment_controller.get_experiment(experiment_id)
    if not state:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    return {
        "id": state.config.id,
        "name": state.config.name,
        "status": state.status,
        "current_round": state.current_round,
        "total_rounds": state.config.rounds,
        "topic": state.config.topic,
        "personas": [p.model_dump() for p in state.config.personas],
        "message_count": len(state.messages),
        "metrics": state.metrics_history[-1] if state.metrics_history else {}
    }


@router.post("/{experiment_id}/start")
async def start_experiment(experiment_id: str):
    """Start experiment"""
    await experiment_controller.start_experiment(experiment_id)
    return {"status": "started"}


@router.post("/{experiment_id}/pause")
async def pause_experiment(experiment_id: str):
    """Pause experiment"""
    await experiment_controller.pause_experiment(experiment_id)
    return {"status": "paused"}


@router.post("/{experiment_id}/resume")
async def resume_experiment(experiment_id: str):
    """Resume experiment"""
    await experiment_controller.resume_experiment(experiment_id)
    return {"status": "resumed"}


@router.post("/{experiment_id}/stop")
async def stop_experiment(experiment_id: str):
    """Stop experiment and generate report"""
    await experiment_controller.stop_experiment(experiment_id)
    return {"status": "stopped"}


@router.post("/{experiment_id}/resources")
async def share_resource(experiment_id: str, request: ResourceShareRequest):
    """Share a resource with personas"""
    resource = ResourceShare(**request.model_dump())
    experiment_controller.add_resource(experiment_id, resource)
    return {"status": "shared", "resource_id": resource.id}


@router.get("/{experiment_id}/report")
async def get_report(experiment_id: str):
    """Get report path"""
    state = experiment_controller.get_experiment(experiment_id)
    if not state:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    report_path = f"./exports/{experiment_id}_report.pdf"
    import os
    if os.path.exists(report_path):
        return {"report_path": report_path, "exists": True}
    return {"report_path": report_path, "exists": False}