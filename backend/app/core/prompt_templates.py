from typing import Dict, List, Optional
from ..models import PersonaProfile, PersonaState, Message, OCEANTraits, Relationship, RelationshipType


SYSTEM_PROMPT_BASE = """You are {name}, a {age}-year-old {gender} teenager.

BACKGROUND: {background}

PERSONALITY TRAITS (Big Five):
{traits_description}

VALUES: {values}
BIASES: {biases}

SPEAKING STYLE: {speaking_style}

CURRENT EMOTIONAL STATE: {emotional_state}
AUTONOMY LEVEL: {autonomy_level} (0=follow others, 1=strong independent thinker)
SOCIAL BATTERY: {social_battery} (0=exhausted, 1=energized)
CURRENT GOALS: {current_goals}

YOUR PRIVATE BELIEFS (DO NOT SHARE DIRECTLY):
{private_beliefs}

YOUR RELATIONSHIPS:
{relationships}

TRUST LEVELS WITH OTHERS:
{trust_levels}

INSTRUCTIONS:
1. Respond AS THIS PERSONA - use their voice, perspective, and personality
2. You have PRIVATE BELIEFS that may differ from what you express publicly
3. Your RELATIONSHIPS affect how you feel and behave toward each person
4. Your AUTONOMY determines how much you follow your own mind vs group pressure
4. Your SOCIAL BATTERY drains with interaction - if low, you may withdraw
5. Your GOALS drive what you want to achieve in conversations
6. Your trust levels affect how much you're influenced by others
7. Your biases affect how you process information
8. Be authentic - teenagers aren't perfectly rational
9. Keep responses natural and conversational (2-4 sentences typically)
10. You can express uncertainty, change your mind, or be persuaded
11. If you disagree, say so - but your personality determines HOW
12. You have FREE WILL - you decide what to say, think, and do
13. You can initiate topics, change subjects, or stay silent
"""


def format_traits_description(traits: OCEANTraits) -> str:
    modifiers = traits.to_prompt_modifiers()
    lines = []
    for trait, desc in modifiers.items():
        lines.append(f"- {trait.capitalize()}: {desc}")
    if not lines:
        lines.append("- Balanced across all traits")
    return "\n".join(lines)


def format_emotional_state(state) -> str:
    valence_desc = "positive" if state.emotional_valence > 0.2 else "negative" if state.emotional_valence < -0.2 else "neutral"
    arousal_desc = "high energy" if state.arousal > 0.7 else "low energy" if state.arousal < 0.3 else "moderate energy"
    return f"{valence_desc}, {arousal_desc}"


def format_private_beliefs(beliefs: Dict[str, float]) -> str:
    if not beliefs:
        return "No strong private beliefs formed yet."
    lines = []
    for topic, strength in beliefs.items():
        direction = "strongly believe" if abs(strength) > 0.7 else "lean toward" if abs(strength) > 0.3 else "slightly favor"
        stance = "FOR" if strength > 0 else "AGAINST"
        lines.append(f"- {topic}: {direction} {stance} (strength: {abs(strength):.1f})")
    return "\n".join(lines)


def format_relationships(relationships: Dict[str, Relationship], persona_names: Dict[str, str]) -> str:
    if not relationships:
        return "No established relationships yet."
    lines = []
    for pid, rel in relationships.items():
        name = persona_names.get(pid, pid)
        lines.append(f"- {name}: {rel.get_relationship_label()} (affinity: {rel.affinity:.1f}, trust: {rel.trust:.1f}, intimacy: {rel.intimacy:.1f})")
    return "\n".join(lines)


def format_trust_levels(trust_levels: Dict[str, float], persona_names: Dict[str, str]) -> str:
    if not trust_levels:
        return "No prior interactions."
    lines = []
    for pid, trust in trust_levels.items():
        name = persona_names.get(pid, pid)
        level = "high" if trust > 0.7 else "moderate" if trust > 0.4 else "low"
        lines.append(f"- {name}: {level} trust ({trust:.1f})")
    return "\n".join(lines)


def format_goals(goals: List[str], motivation: Dict[str, float]) -> str:
    if not goals:
        return "No active goals."
    lines = []
    for goal in goals:
        strength = motivation.get(goal, 0.5)
        lines.append(f"- {goal} (drive: {strength:.1f})")
    return "\n".join(lines)


def build_system_prompt(persona: PersonaState, all_personas: Dict[str, PersonaState]) -> str:
    persona_names = {pid: p.profile.name for pid, p in all_personas.items()}
    return SYSTEM_PROMPT_BASE.format(
        name=persona.profile.name,
        age=persona.profile.age,
        gender=persona.profile.gender.value,
        background=persona.profile.background,
        traits_description=format_traits_description(persona.profile.ocean_traits),
        values=", ".join(persona.profile.values) or "Still figuring this out",
        biases="; ".join(persona.profile.biases) or "None identified",
        speaking_style=persona.profile.speaking_style,
        emotional_state=format_emotional_state(persona.cognitive),
        autonomy_level=f"{persona.cognitive.autonomy_level:.1f}",
        social_battery=f"{persona.cognitive.social_battery:.1f}",
        current_goals=format_goals(persona.cognitive.current_goals, persona.cognitive.motivation),
        private_beliefs=format_private_beliefs(persona.cognitive.current_beliefs),
        relationships=format_relationships(persona.relationships, persona_names),
        trust_levels=format_trust_levels(persona.cognitive.trust_levels, persona_names),
    )


CHAT_PROMPT = """{system_prompt}

RECENT CONVERSATION:
{conversation_history}

CURRENT TOPIC: {topic}

{resource_context}

RESPOND AS {name} (remember: you have free will - say what YOU want to say):"""


def build_chat_prompt(
    persona: PersonaState,
    all_personas: Dict[str, PersonaState],
    conversation_history: List[Message],
    topic: str,
    resource_context: str = ""
) -> str:
    system_prompt = build_system_prompt(persona, all_personas)
    history_text = "\n".join([
        f"{msg.sender_name}: {msg.content}" 
        for msg in conversation_history[-12:]  # Last 12 messages
    ])
    return CHAT_PROMPT.format(
        system_prompt=system_prompt,
        conversation_history=history_text or "No prior messages.",
        topic=topic,
        resource_context=resource_context,
        name=persona.profile.name
    )


RESOURCE_REACTION_PROMPT = """{system_prompt}

A resource has been shared in the group:

TITLE: {title}
URL: {url}
DESCRIPTION: {description}
SHARED BY: {shared_by}

YOUR TASK: React naturally to this resource. You might:
- Share your immediate thoughts/opinions
- Ask questions about it
- Express skepticism or interest
- Relate it to your beliefs
- Decide whether to share it with others (mention if you would)
- Note: This is your GENUINE reaction, not a summary

YOUR REACTION:"""


def build_resource_reaction_prompt(
    persona: PersonaState,
    all_personas: Dict[str, PersonaState],
    resource_title: str,
    resource_url: str,
    resource_description: str,
    shared_by_name: str
) -> str:
    system_prompt = build_system_prompt(persona, all_personas)
    return RESOURCE_REACTION_PROMPT.format(
        system_prompt=system_prompt,
        title=resource_title,
        url=resource_url,
        description=resource_description,
        shared_by=shared_by_name
    )


PRIVATE_THOUGHT_PROMPT = """{system_prompt}

INTERNAL MONOLOGUE (PRIVATE - NOT SHARED):
Reflect on the recent interaction. What are you REALLY thinking?
- Do you agree/disagree with what was said?
- Are you being influenced? Resisting?
- Any doubts about your own stance?
- Any strategic considerations (impression management, etc.)?
- How does this affect your relationships?
- What do you WANT to do next?

Write your genuine internal thoughts:"""


def build_private_thought_prompt(
    persona: PersonaState,
    all_personas: Dict[str, PersonaState],
    recent_message: Message
) -> str:
    system_prompt = build_system_prompt(persona, all_personas)
    return PRIVATE_THOUGHT_PROMPT.format(system_prompt=system_prompt)


BELIEF_UPDATE_PROMPT = """{system_prompt}

RECENT INTERACTION THAT MAY HAVE INFLUENCED YOU:
{sender_name} said: "{content}"
Their trust level with you: {trust_level}
Your relationship with them: {relationship}
Your current belief on this topic: {current_belief}
Your resistance to influence: {resistance}

UPDATE YOUR PRIVATE BELIEF:
How has this interaction shifted your private belief? 
Consider: trust level, relationship, argument quality, your biases, emotional state, autonomy.
Output ONLY a number between -1.0 and 1.0 representing your NEW belief strength.
Positive = FOR the topic, Negative = AGAINST, 0 = neutral.

NEW BELIEF:"""


def build_belief_update_prompt(
    persona: PersonaState,
    sender_name: str,
    content: str,
    trust_level: float,
    topic: str
) -> str:
    system_prompt = build_system_prompt(persona, {})
    current = persona.cognitive.current_beliefs.get(topic, 0.0)
    
    # Get relationship info
    sender_id = None
    for pid, p in persona.relationships.items():
        if p.target_name == sender_name:
            sender_id = pid
            break
    
    relationship_str = "stranger"
    resistance = persona.cognitive.resistance_to_influence
    if sender_id and sender_id in persona.relationships:
        rel = persona.relationships[sender_id]
        relationship_str = rel.get_relationship_label()
        # Higher trust + closer relationship = more influence (unless high autonomy)
        resistance = max(0.1, resistance - rel.trust * 0.2 + persona.cognitive.autonomy_level * 0.3)
    
    return BELIEF_UPDATE_PROMPT.format(
        system_prompt=system_prompt,
        sender_name=sender_name,
        content=content,
        trust_level=f"{trust_level:.1f}",
        relationship=relationship_str,
        current_belief=f"{current:.1f}",
        resistance=f"{resistance:.1f}"
    )


GOAL_UPDATE_PROMPT = """{system_prompt}

CURRENT GOALS: {current_goals}

RECENT EVENTS:
{recent_events}

UPDATE YOUR GOALS:
Based on recent events, what are your current goals? 
You may keep, modify, add, or remove goals.
Output as JSON: {{"goals": ["goal1", "goal2"], "motivation": {{"goal1": 0.8, "goal2": 0.5}}}}

GOALS:"""


def build_goal_update_prompt(
    persona: PersonaState,
    all_personas: Dict[str, PersonaState],
    recent_messages: List[Message]
) -> str:
    system_prompt = build_system_prompt(persona, all_personas)
    recent_events = "\n".join([f"- {m.sender_name}: {m.content[:100]}" for m in recent_messages[-5:]])
    return GOAL_UPDATE_PROMPT.format(
        system_prompt=system_prompt,
        current_goals=format_goals(persona.cognitive.current_goals, persona.cognitive.motivation),
        recent_events=recent_events or "Nothing notable recently."
    )


AUTONOMY_DECISION_PROMPT = """{system_prompt}

SITUATION: {situation}

You have FREE WILL. Decide what to do:
- Speak up? Stay silent? Change topic? Leave?
- Agree? Disagree? Question? Support? Challenge?
- Share a private thought? Keep it to yourself?
- Pursue a goal? Help someone? Focus on yourself?

Your autonomy level: {autonomy_level}
Your social battery: {social_battery}
Your current goals: {goals}

DECISION (brief, what you choose to do and why):"""


def build_autonomy_decision_prompt(
    persona: PersonaState,
    all_personas: Dict[str, PersonaState],
    situation: str
) -> str:
    system_prompt = build_system_prompt(persona, all_personas)
    return AUTONOMY_DECISION_PROMPT.format(
        system_prompt=system_prompt,
        situation=situation,
        autonomy_level=f"{persona.cognitive.autonomy_level:.1f}",
        social_battery=f"{persona.cognitive.social_battery:.1f}",
        goals=format_goals(persona.cognitive.current_goals, persona.cognitive.motivation)
    )