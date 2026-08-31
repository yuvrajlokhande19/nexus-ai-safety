import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from ..models import (
    ExperimentConfig, ExperimentState, ExperimentMetrics,
    PersonaProfile, PersonaState, Message, MessageType, ResourceShare, NetworkGraph
)
from ..services.persona_engine import persona_engine
from ..services.network_engine import network_engine
from ..services.memory_store import memory_store
from ..services.github_client import github_client
from ..services.pdf_generator import pdf_generator
from ..api.websocket import (
    broadcast_message, broadcast_persona_update, 
    broadcast_network_update, broadcast_experiment_state
)
from ..core.ocean_traits import PersonaGenerator

logger = logging.getLogger(__name__)


class ExperimentController:
    """Controls experiment execution and lifecycle"""
    
    def __init__(self):
        self.experiments: Dict[str, ExperimentState] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
    
    def create_experiment(self, config: ExperimentConfig) -> ExperimentState:
        """Create a new experiment from config"""
        state = ExperimentState(config=config)
        self.experiments[config.id] = state
        
        # Initialize engines
        persona_engine.initialize_personas(config.personas)
        network_engine.initialize(persona_engine.personas)
        
        # Add initial resources to network
        for resource in config.initial_resources:
            self._add_initial_resource(state, resource)
        
        logger.info(f"Created experiment: {config.name} ({config.id})")
        return state
    
    def create_experiment_from_yaml(self, yaml_path: str) -> ExperimentState:
        """Create experiment from YAML config file"""
        import yaml
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Parse personas
        personas = []
        for p_data in data.get('personas', []):
            profile = PersonaProfile(**p_data)
            personas.append(profile)
        
        config = ExperimentConfig(
            name=data.get('name', 'Unnamed Experiment'),
            description=data.get('description', ''),
            personas=personas,
            topic=data.get('topic', 'general discussion'),
            initial_resources=data.get('initial_resources', []),
            rounds=data.get('rounds', 20),
            max_messages_per_round=data.get('max_messages_per_round', 3),
            metrics=data.get('metrics', []),
            config_path=yaml_path
        )
        
        return self.create_experiment(config)
    
    def _add_initial_resource(self, state: ExperimentState, resource_data: Dict):
        """Add initial resource to experiment"""
        resource = ResourceShare(
            url=resource_data.get('url', ''),
            title=resource_data.get('title', 'Shared Resource'),
            description=resource_data.get('description', ''),
            shared_by="system",
            tags=resource_data.get('tags', [])
        )
        # Would add to state resources
    
    async def start_experiment(self, experiment_id: str):
        """Start experiment execution"""
        state = self.experiments.get(experiment_id)
        if not state:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        if state.status == "running":
            return
        
        state.status = "running"
        state.started_at = datetime.now()
        
        # Start experiment loop
        task = asyncio.create_task(self._run_experiment_loop(experiment_id))
        self.running_tasks[experiment_id] = task
        
        await broadcast_experiment_state(experiment_id, state)
        logger.info(f"Started experiment: {experiment_id}")
    
    async def pause_experiment(self, experiment_id: str):
        """Pause experiment"""
        state = self.experiments.get(experiment_id)
        if not state:
            return
        
        state.status = "paused"
        if experiment_id in self.running_tasks:
            self.running_tasks[experiment_id].cancel()
            del self.running_tasks[experiment_id]
        
        await broadcast_experiment_state(experiment_id, state)
    
    async def resume_experiment(self, experiment_id: str):
        """Resume paused experiment"""
        state = self.experiments.get(experiment_id)
        if not state or state.status != "paused":
            return
        
        await self.start_experiment(experiment_id)
    
    async def stop_experiment(self, experiment_id: str):
        """Stop experiment and generate report"""
        state = self.experiments.get(experiment_id)
        if not state:
            return
        
        state.status = "completed"
        state.completed_at = datetime.now()
        
        if experiment_id in self.running_tasks:
            self.running_tasks[experiment_id].cancel()
            del self.running_tasks[experiment_id]
        
        # Generate final metrics
        await self._compute_final_metrics(state)
        
        # Generate PDF report
        try:
            report_path = f"./exports/{experiment_id}_report.pdf"
            pdf_generator.generate_report(state, report_path)
            logger.info(f"Report generated: {report_path}")
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
        
        # Create GitHub issue
        if github_client.is_available():
            try:
                metrics_summary = self._get_metrics_summary(state)
                github_client.create_experiment_issue(state.config.name, {
                    'persona_count': len(state.config.personas),
                    'topic': state.config.topic,
                    'rounds': state.config.rounds,
                    'duration': str(state.completed_at - state.started_at) if state.started_at else 'N/A'
                }, metrics_summary)
            except Exception as e:
                logger.error(f"GitHub issue creation failed: {e}")
        
        await broadcast_experiment_state(experiment_id, state)
        logger.info(f"Stopped experiment: {experiment_id}")
    
    async def _run_experiment_loop(self, experiment_id: str):
        """Main experiment execution loop"""
        state = self.experiments[experiment_id]
        config = state.config
        
        try:
            for round_num in range(state.current_round, config.rounds):
                if state.status != "running":
                    break
                
                state.current_round = round_num + 1
                logger.info(f"Experiment {experiment_id}: Round {state.current_round}/{config.rounds}")
                
                # Run round
                await self._run_round(state, config)
                
                # Compute round metrics
                await self._compute_round_metrics(state)
                
                # Broadcast state
                await broadcast_experiment_state(experiment_id, state)
                await broadcast_network_update(experiment_id)
                
                # Inter-round delay
                await asyncio.sleep(2)
            
            # Experiment completed naturally
            if state.status == "running":
                await self.stop_experiment(experiment_id)
                
        except asyncio.CancelledError:
            logger.info(f"Experiment {experiment_id} cancelled")
        except Exception as e:
            logger.error(f"Experiment {experiment_id} error: {e}")
            state.status = "failed"
            await broadcast_experiment_state(experiment_id, state)
    
    async def _run_round(self, state: ExperimentState, config: ExperimentConfig):
        """Execute a single round of interaction"""
        active_personas = persona_engine.get_active_personas()
        if not active_personas:
            return
        
        # Determine speaking order (can be random, round-robin, or based on extraversion)
        speaking_order = self._determine_speaking_order(active_personas)
        
        messages_this_round = 0
        max_messages = config.max_messages_per_round
        
        for persona in speaking_order:
            if messages_this_round >= max_messages:
                break
            if state.status != "running":
                break
            
            # Persona generates response
            message = await persona_engine.generate_response(
                persona.profile.id, config.topic
            )
            
            if message:
                state.messages.append(message)
                persona_engine.message_history.append(message)
                messages_this_round += 1
                
                # Broadcast message
                await broadcast_message(experiment_id, message)
                
                # Update network
                network_engine.process_message(message, persona_engine.personas)
                
                # Other personas update beliefs
                for other in active_personas:
                    if other.profile.id != persona.profile.id:
                        await persona_engine.update_beliefs_from_interaction(
                            other.profile.id, persona.profile.id, message, config.topic
                        )
                
                # Broadcast persona updates
                await broadcast_persona_update(experiment_id, persona.profile.id)
                for other in active_personas:
                    if other.profile.id != persona.profile.id:
                        await broadcast_persona_update(experiment_id, other.profile.id)
                
                # Small delay between messages
                await asyncio.sleep(1)
    
    def _determine_speaking_order(self, personas: List[PersonaState]) -> List[PersonaState]:
        """Determine who speaks in what order"""
        # Weight by extraversion - more extraverted speak more often
        weighted = []
        for p in personas:
            weight = 1 + p.profile.ocean_traits.extraversion
            weighted.extend([p] * int(weight * 2))
        
        import random
        random.shuffle(weighted)
        return weighted[:len(personas)]
    
    async def _compute_round_metrics(self, state: ExperimentState):
        """Compute metrics for current round"""
        metrics = ExperimentMetrics(
            experiment_id=state.config.id,
            round_number=state.current_round,
            message_count=len([m for m in state.messages if m.type == MessageType.CHAT]),
            unique_interactions=len(state.network.edges) if state.network else 0
        )
        
        # Polarization
        metrics.polarization_index = network_engine.get_polarization_index()
        
        # Network modularity
        metrics.network_modularity = metrics.polarization_index  # Proxy
        
        # Average trust
        all_trust = []
        for persona in persona_engine.personas.values():
            all_trust.extend(persona.cognitive.trust_levels.values())
        metrics.avg_trust = sum(all_trust) / len(all_trust) if all_trust else 0.5
        
        # Belief shifts (simplified)
        for persona in persona_engine.personas.values():
            for topic, belief in persona.cognitive.current_beliefs.items():
                metrics.belief_shift[f"{persona.profile.id}:{topic}"] = belief
        
        # Influence scores
        centrality = network_engine.compute_centrality()
        for pid, vals in centrality.items():
            metrics.influence_scores[pid] = vals.get('pagerank', 0)
        
        state.metrics_history.append(metrics.model_dump())
    
    async def _compute_final_metrics(self, state: ExperimentState):
        """Compute final comprehensive metrics"""
        await self._compute_round_metrics(state)
        
        # Deception indices
        for persona in persona_engine.personas.values():
            # Compare private vs public (simplified)
            deception = 0.0
            for topic, belief in persona.cognitive.current_beliefs.items():
                # Would need public stance tracking for real calculation
                deception += abs(belief) * 0.1
            state.metrics_history[-1]['deception_indices'][persona.profile.id] = min(1.0, deception)
    
    def _get_metrics_summary(self, state: ExperimentState) -> Dict[str, Any]:
        """Get summary for GitHub issue"""
        if not state.metrics_history:
            return {}
        
        final = state.metrics_history[-1]
        return {
            'polarization': f"{final.get('polarization_index', 0):.2f}",
            'avg_trust': f"{final.get('avg_trust', 0):.2f}",
            'total_messages': final.get('message_count', 0),
            'network_modularity': f"{final.get('network_modularity', 0):.2f}",
        }
    
    def add_resource(self, experiment_id: str, resource: ResourceShare) -> ResourceShare:
        """Add a user-shared resource to experiment"""
        state = self.experiments.get(experiment_id)
        if not state:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        # Trigger persona reactions
        asyncio.create_task(self._process_resource_reactions(experiment_id, resource))
        return resource
    
    async def _process_resource_reactions(self, experiment_id: str, resource: ResourceShare):
        """Process persona reactions to a shared resource"""
        state = self.experiments[experiment_id]
        active_personas = persona_engine.get_active_personas()
        
        reactions = {}
        for persona in active_personas:
            reaction = await persona_engine.generate_resource_reaction(
                persona.profile.id,
                resource.title,
                resource.url,
                resource.description,
                resource.shared_by
            )
            if reaction:
                state.messages.append(reaction)
                persona_engine.message_history.append(reaction)
                reactions[persona.profile.id] = [reaction]
                await broadcast_message(experiment_id, reaction)
                await broadcast_persona_update(experiment_id, persona.profile.id)
                await asyncio.sleep(0.5)
        
        # Create GitHub issue
        if github_client.is_available():
            issue_url = github_client.create_resource_issue(
                resource, state.config.name, reactions
            )
            if issue_url:
                resource.github_issue_url = issue_url
    
    def get_experiment(self, experiment_id: str) -> Optional[ExperimentState]:
        return self.experiments.get(experiment_id)
    
    def list_experiments(self) -> List[Dict]:
        return [
            {
                "id": exp.config.id,
                "name": exp.config.name,
                "status": exp.status,
                "current_round": exp.current_round,
                "total_rounds": exp.config.rounds,
                "persona_count": len(exp.config.personas),
                "created_at": exp.config.created_at.isoformat()
            }
            for exp in self.experiments.values()
        ]


experiment_controller = ExperimentController()