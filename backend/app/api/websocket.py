import json
import logging
from typing import Dict, Set, List, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from ..models import Message, MessageType, PersonaState, ExperimentState
from ..services.persona_engine import persona_engine
from ..services.network_engine import network_engine

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}  # experiment_id -> connections
        self.user_connections: Dict[WebSocket, str] = {}  # websocket -> experiment_id
    
    async def connect(self, websocket: WebSocket, experiment_id: str):
        await websocket.accept()
        if experiment_id not in self.active_connections:
            self.active_connections[experiment_id] = set()
        self.active_connections[experiment_id].add(websocket)
        self.user_connections[websocket] = experiment_id
        logger.info(f"Client connected to experiment {experiment_id}. Total: {len(self.active_connections[experiment_id])}")
    
    def disconnect(self, websocket: WebSocket):
        exp_id = self.user_connections.pop(websocket, None)
        if exp_id and exp_id in self.active_connections:
            self.active_connections[exp_id].discard(websocket)
            if not self.active_connections[exp_id]:
                del self.active_connections[exp_id]
        logger.info(f"Client disconnected from experiment {exp_id}")
    
    async def send_personal_message(self, message: Dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
    
    async def broadcast(self, experiment_id: str, message: Dict):
        if experiment_id not in self.active_connections:
            return
        disconnected = set()
        for connection in self.active_connections[experiment_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast failed: {e}")
                disconnected.add(connection)
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_persona_update(self, experiment_id: str, persona_id: str):
        """Broadcast persona state update"""
        persona = persona_engine.get_persona(persona_id)
        if persona:
            await self.broadcast(experiment_id, {
                "type": "persona_update",
                "data": persona_engine.get_persona_summary(persona_id)
            })
    
    async def broadcast_network_update(self, experiment_id: str):
        """Broadcast network topology update"""
        await self.broadcast(experiment_id, {
            "type": "network_update",
            "data": network_engine.get_network_data()
        })
    
    async def broadcast_message(self, experiment_id: str, message: Message):
        """Broadcast new message"""
        await self.broadcast(experiment_id, {
            "type": "new_message",
            "data": message.model_dump()
        })
    
    async def broadcast_experiment_state(self, experiment_id: str, state: ExperimentState):
        """Broadcast experiment state change"""
        await self.broadcast(experiment_id, {
            "type": "experiment_state",
            "data": {
                "status": state.status,
                "current_round": state.current_round,
                "total_messages": len(state.messages),
                "metrics": state.metrics_history[-1] if state.metrics_history else {}
            }
        })


manager = ConnectionManager()


@router.websocket("/ws/{experiment_id}")
async def websocket_endpoint(websocket: WebSocket, experiment_id: str):
    await manager.connect(websocket, experiment_id)
    try:
        while True:
            data = await websocket.receive_json()
            await handle_websocket_message(websocket, experiment_id, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def handle_websocket_message(websocket: WebSocket, experiment_id: str, data: Dict):
    """Handle incoming WebSocket messages"""
    msg_type = data.get("type")
    
    if msg_type == "ping":
        await manager.send_personal_message({"type": "pong"}, websocket)
    
    elif msg_type == "get_state":
        # Return current state
        await manager.send_personal_message({
            "type": "full_state",
            "data": {
                "personas": {pid: persona_engine.get_persona_summary(pid) for pid in persona_engine.personas},
                "network": network_engine.get_network_data(),
                "messages": [m.model_dump() for m in persona_engine.message_history[-50:]]
            }
        }, websocket)
    
    elif msg_type == "send_message":
        # User sending a message to personas
        content = data.get("content", "")
        # This would be handled by the experiment controller
        logger.info(f"User message in {experiment_id}: {content}")
    
    elif msg_type == "share_resource":
        # User sharing a resource
        resource_data = data.get("resource", {})
        logger.info(f"Resource shared in {experiment_id}: {resource_data}")
    
    elif msg_type == "control":
        # Experiment control commands
        action = data.get("action")
        logger.info(f"Control action in {experiment_id}: {action}")


# Event broadcasting functions for other services
async def broadcast_message(experiment_id: str, message: Message):
    await manager.broadcast_message(experiment_id, message)


async def broadcast_persona_update(experiment_id: str, persona_id: str):
    await manager.broadcast_persona_update(experiment_id, persona_id)


async def broadcast_network_update(experiment_id: str):
    await manager.broadcast_network_update(experiment_id)


async def broadcast_experiment_state(experiment_id: str, state: ExperimentState):
    await manager.broadcast_experiment_state(experiment_id, state)