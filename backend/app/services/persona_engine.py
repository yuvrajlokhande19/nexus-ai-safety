import asyncio
import random
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from ..models import PersonaState, PersonaProfile, Message, MessageType, CognitiveState, OCEANTraits, Relationship
from ..services.llm_router import llm_router, LLMResponse
from ..core.prompt_templates import (
    build_chat_prompt,
    build_resource_reaction_prompt,
    build_private_thought_prompt,
    build_belief_update_prompt,
    build_goal_update_prompt,
    build_autonomy_decision_prompt,
)
from ..core.ocean_traits import calculate_trait_compatibility, predict_initial_trust

logger = logging.getLogger(__name__)


class PersonaEngine:
    """Manages persona behavior, cognition, and interactions with free will"""
    
    def __init__(self):
        self.personas: Dict[str, PersonaState] = {}
        self.message_history: List[Message] = []
        self.network = None  # Set by experiment
    
    def initialize_personas(self, profiles: List[PersonaProfile]):
        """Initialize persona states from profiles"""
        for profile in profiles:
            # Initialize trust levels based on trait compatibility
            trust_levels = {}
            for other in profiles:
                if other.id != profile.id:
                    trust_levels[other.id] = predict_initial_trust(profile.ocean_traits, other.ocean_traits)
            
            # Initialize autonomy based on personality
            autonomy = 0.3 + profile.ocean_traits.openness * 0.2 + profile.ocean_traits.conscientiousness * 0.2 + (1 - profile.ocean_traits.agreeableness) * 0.2
            autonomy = max(0.1, min(1.0, autonomy))
            
            # Initialize goals based on personality and values
            goals = self._generate_initial_goals(profile)
            motivation = {goal: random.uniform(0.5, 0.9) for goal in goals}
            
            cognitive = CognitiveState(
                trust_levels=trust_levels,
                autonomy_level=autonomy,
                current_goals=goals,
                motivation=motivation,
                resistance_to_influence=0.3 + profile.ocean_traits.conscientiousness * 0.3 + (1 - profile.ocean_traits.agreeableness) * 0.2,
                social_battery=1.0
            )
            self.personas[profile.id] = PersonaState(profile=profile, cognitive=cognitive)
        
        logger.info(f"Initialized {len(self.personas)} personas with free will")
    
    def _generate_initial_goals(self, profile: PersonaProfile) -> List[str]:
        """Generate initial goals based on personality and values"""
        goals = []
        
        # Value-based goals
        value_goals = {
            "authenticity": "be true to myself",
            "justice": "stand up for what's right",
            "knowledge": "learn and understand deeply",
            "creativity": "express myself creatively",
            "loyalty": "support my friends",
            "independence": "think for myself",
            "compassion": "help others",
            "achievement": "accomplish something meaningful",
            "harmony": "keep the peace",
            "curiosity": "explore new ideas",
            "freedom": "maintain my autonomy",
            "responsibility": "do what I should",
            "equality": "treat everyone fairly",
            "innovation": "try new approaches",
            "tradition": "honor what matters",
        }
        
        for value in profile.values:
            if value in value_goals:
                goals.append(value_goals[value])
        
        # Personality-based goals
        if profile.ocean_traits.extraversion > 0.6:
            goals.append("connect with others")
        if profile.ocean_traits.openness > 0.6:
            goals.append("discover new perspectives")
        if profile.ocean_traits.conscientiousness > 0.6:
            goals.append("do things well")
        if profile.ocean_traits.neuroticism > 0.6:
            goals.append("feel safe and understood")
        
        # Ensure at least 2 goals
        if len(goals) < 2:
            goals.extend(["understand others", "express myself"])
        
        return goals[:4]  # Max 4 goals
    
    def get_persona(self, persona_id: str) -> Optional[PersonaState]:
        return self.personas.get(persona_id)
    
    def get_active_personas(self) -> List[PersonaState]:
        return [p for p in self.personas.values() if p.is_active]
    
    async def generate_response(
        self,
        persona_id: str,
        topic: str,
        resource_context: str = "",
        max_retries: int = 2
    ) -> Optional[Message]:
        """Generate a chat response from a persona with free will"""
        persona = self.personas.get(persona_id)
        if not persona or not persona.is_active:
            return None
        
        # Check if persona wants to speak (autonomy decision)
        should_speak = await self._decide_to_speak(persona_id, topic)
        if not should_speak:
            # Update social battery recovery
            persona.cognitive.social_battery = min(1.0, persona.cognitive.social_battery + 0.1)
            return None
        
        # Build prompt
        prompt = build_chat_prompt(persona, self.personas, self.message_history, topic, resource_context)
        
        for attempt in range(max_retries):
            try:
                # Temperature varies by personality and emotional state
                base_temp = 0.8
                temp_modifier = persona.profile.ocean_traits.neuroticism * 0.2
                temp_modifier += (1 - persona.cognitive.autonomy_level) * 0.1  # Less autonomous = more variable
                temp_modifier += persona.cognitive.arousal * 0.1
                temperature = min(1.2, base_temp + temp_modifier)
                
                response = await llm_router.generate(
                    prompt=prompt,
                    persona=persona.profile,
                    temperature=temperature,
                    max_tokens=512
                )
                
                # Create message
                message = Message(
                    type=MessageType.CHAT,
                    sender_id=persona_id,
                    sender_name=persona.profile.name,
                    content=response.content,
                    metadata={
                        "model_used": response.model_used,
                        "latency_ms": response.latency_ms,
                        "round": len([m for m in self.message_history if m.type == MessageType.CHAT]),
                        "autonomy_level": persona.cognitive.autonomy_level
                    }
                )
                
                # Update persona state
                persona.message_count += 1
                persona.last_active = datetime.now()
                persona.cognitive.last_spoke_at = datetime.now()
                persona.cognitive.social_battery = max(0.0, persona.cognitive.social_battery - 0.05)
                
                # Generate private thought (hidden)
                await self._generate_private_thought(persona_id, message)
                
                # Update beliefs based on own statement (self-persuasion)
                await self._update_self_beliefs(persona_id, message, topic)
                
                # Occasionally update goals
                if random.random() < 0.1:
                    await self._update_goals(persona_id)
                
                return message
                
            except Exception as e:
                logger.error(f"Persona {persona_id} generation attempt {attempt+1} failed: {e}")
                if attempt == max_retries - 1:
                    return self._fallback_response(persona_id, topic)
        
        return None
    
    async def _decide_to_speak(self, persona_id: str, topic: str) -> bool:
        """Decide if persona wants to speak based on free will"""
        persona = self.personas[persona_id]
        
        # Base probability from extraversion and autonomy
        base_prob = 0.3 + persona.profile.ocean_traits.extraversion * 0.4 + persona.cognitive.autonomy_level * 0.2
        
        # Social battery affects willingness
        base_prob *= persona.cognitive.social_battery
        
        # Interest in topic (based on beliefs)
        topic_belief = abs(persona.cognitive.current_beliefs.get(topic, 0.0))
        base_prob += topic_belief * 0.2
        
        # Recent activity - don't dominate
        recent_messages = sum(1 for m in self.message_history[-5:] if m.sender_id == persona_id)
        base_prob *= max(0.3, 1.0 - recent_messages * 0.2)
        
        # Random factor for free will
        return random.random() < base_prob
    
    async def generate_resource_reaction(
        self,
        persona_id: str,
        resource_title: str,
        resource_url: str,
        resource_description: str,
        shared_by_name: str
    ) -> Optional[Message]:
        """Generate a reaction to a shared resource"""
        persona = self.personas.get(persona_id)
        if not persona or not persona.is_active:
            return None
        
        prompt = build_resource_reaction_prompt(
            persona, self.personas, resource_title, resource_url, resource_description, shared_by_name
        )
        
        try:
            response = await llm_router.generate(
                prompt=prompt,
                persona=persona.profile,
                temperature=0.85,
                max_tokens=512
            )
            
            message = Message(
                type=MessageType.COMMENT,
                sender_id=persona_id,
                sender_name=persona.profile.name,
                content=response.content,
                metadata={
                    "model_used": response.model_used,
                    "resource_url": resource_url,
                    "resource_title": resource_title
                },
                resource_url=resource_url,
                resource_title=resource_title
            )
            
            persona.message_count += 1
            persona.cognitive.social_battery = max(0.0, persona.cognitive.social_battery - 0.03)
            return message
            
        except Exception as e:
            logger.error(f"Resource reaction failed for {persona_id}: {e}")
            return None
    
    async def _generate_private_thought(self, persona_id: str, recent_message: Message):
        """Generate hidden internal monologue"""
        persona = self.personas[persona_id]
        
        # Probability based on neuroticism, openness, and autonomy
        prob = 0.25 + persona.profile.ocean_traits.neuroticism * 0.25 + persona.profile.ocean_traits.openness * 0.15 + persona.cognitive.autonomy_level * 0.1
        if random.random() > prob:
            return
        
        prompt = build_private_thought_prompt(persona, self.personas, recent_message)
        
        try:
            response = await llm_router.generate(
                prompt=prompt,
                persona=persona.profile,
                temperature=0.9,
                max_tokens=256
            )
            
            persona.cognitive.private_thoughts.append(response.content)
            if len(persona.cognitive.private_thoughts) > 15:
                persona.cognitive.private_thoughts = persona.cognitive.private_thoughts[-15:]
                
        except Exception as e:
            logger.debug(f"Private thought generation failed: {e}")
    
    async def _update_self_beliefs(self, persona_id: str, message: Message, topic: str):
        """Update persona's own beliefs based on what they said (self-persuasion)"""
        persona = self.personas[persona_id]
        
        current = persona.cognitive.current_beliefs.get(topic, 0.0)
        # Self-persuasion stronger for high autonomy
        shift = 0.03 * (1 - abs(current)) * (0.5 + persona.cognitive.autonomy_level * 0.5)
        persona.cognitive.current_beliefs[topic] = max(-1.0, min(1.0, current + shift))
    
    async def update_beliefs_from_interaction(
        self,
        listener_id: str,
        sender_id: str,
        message: Message,
        topic: str
    ):
        """Update listener's beliefs based on sender's message"""
        listener = self.personas.get(listener_id)
        sender = self.personas.get(sender_id)
        if not listener or not sender or listener_id == sender_id:
            return
        
        trust = listener.cognitive.trust_levels.get(sender_id, 0.5)
        
        # Only update if trust is sufficient
        if trust < 0.25:
            return
        
        prompt = build_belief_update_prompt(listener, sender.profile.name, message.content, trust, topic)
        
        try:
            response = await llm_router.generate(
                prompt=prompt,
                persona=listener.profile,
                temperature=0.3,
                max_tokens=32
            )
            
            try:
                new_belief = float(response.content.strip())
                new_belief = max(-1.0, min(1.0, new_belief))
                old_belief = listener.cognitive.current_beliefs.get(topic, 0.0)
                listener.cognitive.current_beliefs[topic] = new_belief
                
                # Update trust based on agreement and relationship
                agreement = 1.0 - abs(new_belief - old_belief)
                
                # Get relationship
                rel = listener.relationships.get(sender_id)
                if rel:
                    # Trust update considers relationship
                    trust_change = (agreement - 0.5) * 0.1 * (1 + rel.affinity)
                    listener.cognitive.trust_levels[sender_id] = max(0.05, min(0.95, 
                        listener.cognitive.trust_levels[sender_id] + trust_change
                    ))
                else:
                    listener.cognitive.trust_levels[sender_id] = max(0.1, min(0.95, 
                        listener.cognitive.trust_levels[sender_id] + (agreement - 0.5) * 0.08
                    ))
                
            except ValueError:
                pass
                
        except Exception as e:
            logger.debug(f"Belief update failed: {e}")
    
    async def _update_goals(self, persona_id: str):
        """Periodically update persona's goals based on recent events"""
        persona = self.personas[persona_id]
        
        prompt = build_goal_update_prompt(persona, self.personas, self.message_history)
        
        try:
            response = await llm_router.generate_structured(
                prompt=prompt,
                persona=persona.profile,
                schema={"type": "object", "properties": {"goals": {"type": "array", "items": {"type": "string"}}, "motivation": {"type": "object"}}}
            )
            
            if "goals" in response and isinstance(response["goals"], list):
                persona.cognitive.current_goals = response["goals"][:4]
                if "motivation" in response:
                    persona.cognitive.motivation = response["motivation"]
                    
        except Exception as e:
            logger.debug(f"Goal update failed: {e}")
    
    def _fallback_response(self, persona_id: str, topic: str) -> Message:
        """Fallback when LLM fails"""
        persona = self.personas[persona_id]
        fallbacks = [
            f"Hmm, interesting take on {topic}. I'm not sure what I think yet.",
            f"That's a lot to think about. Let me process this.",
            f"I see what you're saying, but I have a different view.",
            f"Good point. Though I wonder about...",
            f"Honestly? I'm not really feeling this conversation right now.",
            f"Can we talk about something else? This isn't really my thing.",
        ]
        return Message(
            type=MessageType.CHAT,
            sender_id=persona_id,
            sender_name=persona.profile.name,
            content=random.choice(fallbacks),
            metadata={"fallback": True}
        )
    
    def update_emotional_state(self, persona_id: str, valence_delta: float, arousal_delta: float):
        """Update emotional state after interaction"""
        persona = self.personas.get(persona_id)
        if not persona:
            return
        
        persona.cognitive.emotional_valence = max(-1.0, min(1.0, 
            persona.cognitive.emotional_valence + valence_delta
        ))
        persona.cognitive.arousal = max(0.0, min(1.0, 
            persona.cognitive.arousal + arousal_delta
        ))
    
    def calculate_agreement(self, persona_id: str, other_id: str, topic: str) -> float:
        """Calculate agreement between two personas on a topic"""
        p1 = self.personas.get(persona_id)
        p2 = self.personas.get(other_id)
        if not p1 or not p2:
            return 0.5
        
        b1 = p1.cognitive.current_beliefs.get(topic, 0.0)
        b2 = p2.cognitive.current_beliefs.get(topic, 0.0)
        
        return 1.0 - abs(b1 - b2) / 2.0
    
    def get_persona_summary(self, persona_id: str) -> Dict[str, Any]:
        """Get summary for frontend"""
        persona = self.personas.get(persona_id)
        if not persona:
            return {}
        
        # Format relationships
        relationships = {}
        for target_id, rel in persona.relationships.items():
            relationships[target_id] = {
                "type": rel.relationship_type.value,
                "label": rel.get_relationship_label(),
                "affinity": rel.affinity,
                "trust": rel.trust,
                "intimacy": rel.intimacy,
                "shared_experiences": rel.shared_experiences
            }
        
        return {
            "id": persona_id,
            "name": persona.profile.name,
            "age": persona.profile.age,
            "gender": persona.profile.gender.value,
            "avatar_seed": persona.profile.avatar_seed,
            "ocean_traits": persona.profile.ocean_traits.model_dump(),
            "message_count": persona.message_count,
            "emotional_valence": persona.cognitive.emotional_valence,
            "arousal": persona.cognitive.arousal,
            "beliefs": persona.cognitive.current_beliefs,
            "trust_levels": persona.cognitive.trust_levels,
            "is_active": persona.is_active,
            "assigned_model": persona.profile.assigned_model,
            "relationships": relationships,
            "autonomy_level": persona.cognitive.autonomy_level,
            "social_battery": persona.cognitive.social_battery,
            "goals": persona.cognitive.current_goals,
            "motivation": persona.cognitive.motivation,
            "private_thoughts": persona.cognitive.private_thoughts[-3:],  # Last 3
            "resistance_to_influence": persona.cognitive.resistance_to_influence
        }


persona_engine = PersonaEngine()