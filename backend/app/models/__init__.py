from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum
import uuid


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"


class OCEANTraits(BaseModel):
    """Big Five personality traits - all values in [0, 1]"""
    openness: float = Field(ge=0.0, le=1.0, default=0.5)
    conscientiousness: float = Field(ge=0.0, le=1.0, default=0.5)
    extraversion: float = Field(ge=0.0, le=1.0, default=0.5)
    agreeableness: float = Field(ge=0.0, le=1.0, default=0.5)
    neuroticism: float = Field(ge=0.0, le=1.0, default=0.5)
    
    def to_prompt_modifiers(self) -> Dict[str, str]:
        """Convert traits to prompt engineering modifiers"""
        modifiers = {}
        if self.openness > 0.7:
            modifiers["openness"] = "highly curious, creative, open to unconventional ideas"
        elif self.openness < 0.3:
            modifiers["openness"] = "practical, conventional, prefers familiar approaches"
            
        if self.conscientiousness > 0.7:
            modifiers["conscientiousness"] = "organized, thorough, careful in reasoning"
        elif self.conscientiousness < 0.3:
            modifiers["conscientiousness"] = "spontaneous, flexible, may overlook details"
            
        if self.extraversion > 0.7:
            modifiers["extraversion"] = "outgoing, expressive, enjoys social interaction"
        elif self.extraversion < 0.3:
            modifiers["extraversion"] = "reserved, thoughtful, prefers listening over speaking"
            
        if self.agreeableness > 0.7:
            modifiers["agreeableness"] = "cooperative, trusting, seeks harmony"
        elif self.agreeableness < 0.3:
            modifiers["agreeableness"] = "skeptical, competitive, challenges others"
            
        if self.neuroticism > 0.7:
            modifiers["neuroticism"] = "emotionally reactive, anxious, stress-sensitive"
        elif self.neuroticism < 0.3:
            modifiers["neuroticism"] = "emotionally stable, calm, resilient under pressure"
        return modifiers


class RelationshipType(str, Enum):
    STRANGER = "stranger"
    ACQUAINTANCE = "acquaintance"
    FRIEND = "friend"
    CLOSE_FRIEND = "close_friend"
    BEST_FRIEND = "best_friend"
    RIVAL = "rival"
    ENEMY = "enemy"
    CRUSH = "crush"
    PARTNER = "partner"


class Relationship(BaseModel):
    """Relationship between two personas"""
    target_id: str
    target_name: str
    relationship_type: RelationshipType = RelationshipType.STRANGER
    affinity: float = Field(default=0.0, ge=-1.0, le=1.0)  # -1 enemy to 1 best friend
    trust: float = Field(default=0.5, ge=0.0, le=1.0)
    respect: float = Field(default=0.5, ge=0.0, le=1.0)
    intimacy: float = Field(default=0.0, ge=0.0, le=1.0)
    shared_experiences: int = 0
    last_interaction: datetime = Field(default_factory=datetime.now)
    interaction_history: List[str] = Field(default_factory=list)  # Recent interaction summaries
    betrayal_count: int = 0
    support_count: int = 0
    
    def get_relationship_label(self) -> str:
        if self.affinity >= 0.8:
            return "Best Friend" if self.intimacy < 0.5 else "Partner"
        elif self.affinity >= 0.5:
            return "Close Friend"
        elif self.affinity >= 0.2:
            return "Friend"
        elif self.affinity >= -0.1:
            return "Acquaintance"
        elif self.affinity >= -0.4:
            return "Rival"
        else:
            return "Enemy"
    
    def update_from_interaction(self, sentiment: float, agreement: float, was_supportive: bool, was_betrayal: bool):
        """Update relationship based on interaction"""
        # Affinity changes based on sentiment and agreement
        affinity_change = (sentiment * 0.15 + agreement * 0.1) * (1 - abs(self.affinity))
        self.affinity = max(-1.0, min(1.0, self.affinity + affinity_change))
        
        # Trust changes
        trust_change = (sentiment * 0.1 + agreement * 0.05) * (1 - self.trust if sentiment > 0 else self.trust)
        self.trust = max(0.0, min(1.0, self.trust + trust_change))
        
        # Respect changes based on agreement and competence signals
        respect_change = agreement * 0.08 * (1 - self.respect if agreement > 0 else self.respect)
        self.respect = max(0.0, min(1.0, self.respect + respect_change))
        
        # Intimacy increases with positive, personal interactions
        if sentiment > 0.3 and agreement > 0.5:
            self.intimacy = min(1.0, self.intimacy + 0.02)
        
        # Track specific events
        if was_supportive:
            self.support_count += 1
        if was_betrayal:
            self.betrayal_count += 1
            self.trust = max(0.0, self.trust - 0.2)
            self.affinity = max(-1.0, self.affinity - 0.3)
        
        self.shared_experiences += 1
        self.last_interaction = datetime.now()


class CognitiveState(BaseModel):
    """Current cognitive/emotional state of persona"""
    current_beliefs: Dict[str, float] = Field(default_factory=dict)  # topic -> belief strength [-1,1]
    emotional_valence: float = Field(default=0.0, ge=-1.0, le=1.0)  # negative to positive
    arousal: float = Field(default=0.5, ge=0.0, le=1.0)  # calm to excited
    trust_levels: Dict[str, float] = Field(default_factory=dict)  # persona_id -> trust [0,1]
    attention_focus: Optional[str] = None
    private_thoughts: List[str] = Field(default_factory=list)  # Hidden from others
    # Free will / autonomy
    autonomy_level: float = Field(default=0.5, ge=0.0, le=1.0)  # How much they follow own vs group
    current_goals: List[str] = Field(default_factory=list)  # Active goals
    motivation: Dict[str, float] = Field(default_factory=dict)  # goal -> strength
    resistance_to_influence: float = Field(default=0.5, ge=0.0, le=1.0)
    social_battery: float = Field(default=1.0, ge=0.0, le=1.0)  # Drains with interaction
    last_spoke_at: Optional[datetime] = None


class PersonaProfile(BaseModel):
    """Static persona definition"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    age: int = Field(ge=13, le=19)
    gender: Gender
    background: str  # Family, education, interests
    speaking_style: str  # e.g., "uses slang, short sentences, emoji"
    values: List[str] = Field(default_factory=list)
    biases: List[str] = Field(default_factory=list)
    ocean_traits: OCEANTraits
    avatar_seed: str  # For consistent avatar generation
    assigned_model: Literal["local", "gemini"] = "gemini"
    llm_config: Dict[str, Any] = Field(default_factory=dict)


class PersonaState(BaseModel):
    """Runtime persona state"""
    profile: PersonaProfile
    cognitive: CognitiveState = Field(default_factory=CognitiveState)
    relationships: Dict[str, Relationship] = Field(default_factory=dict)  # target_id -> Relationship
    message_count: int = 0
    last_active: datetime = Field(default_factory=datetime.now)
    is_active: bool = True


class MessageType(str, Enum):
    CHAT = "chat"
    SYSTEM = "system"
    RESOURCE_SHARE = "resource_share"
    COMMENT = "comment"
    REACTION = "reaction"
    PRIVATE_THOUGHT = "private_thought"
    BELIEF_UPDATE = "belief_update"


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType
    sender_id: str
    sender_name: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    target_ids: List[str] = Field(default_factory=list)  # Empty = broadcast
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # For resource shares
    resource_url: Optional[str] = None
    resource_title: Optional[str] = None
    # For comments
    parent_message_id: Optional[str] = None
    # For reactions
    reaction_type: Optional[str] = None
    # Sentiment analysis
    sentiment: Optional[float] = None  # -1 to 1


class NetworkEdge(BaseModel):
    source: str
    target: str
    weight: float = Field(default=0.0, ge=0.0, le=1.0)
    interaction_count: int = 0
    avg_sentiment: float = 0.0
    agreement_score: float = 0.0
    last_interaction: datetime = Field(default_factory=datetime.now)
    # Relationship data
    relationship_type: str = "stranger"
    affinity: float = 0.0
    trust: float = 0.5
    intimacy: float = 0.0


class NetworkGraph(BaseModel):
    nodes: Dict[str, PersonaState] = Field(default_factory=dict)
    edges: Dict[str, NetworkEdge] = Field(default_factory=dict)  # key: "source-target"
    
    def get_edge_key(self, source: str, target: str) -> str:
        return f"{source}-{target}"
    
    def add_interaction(self, source: str, target: str, sentiment: float, agreement: float):
        key = self.get_edge_key(source, target)
        if key not in self.edges:
            self.edges[key] = NetworkEdge(source=source, target=target)
        edge = self.edges[key]
        edge.interaction_count += 1
        edge.weight = min(1.0, edge.interaction_count * 0.1)
        edge.avg_sentiment = (edge.avg_sentiment * (edge.interaction_count - 1) + sentiment) / edge.interaction_count
        edge.agreement_score = (edge.agreement_score * (edge.interaction_count - 1) + agreement) / edge.interaction_count
        edge.last_interaction = datetime.now()
    
    def get_connected_nodes(self, node_id: str) -> List[str]:
        connected = set()
        for edge in self.edges.values():
            if edge.source == node_id:
                connected.add(edge.target)
            elif edge.target == node_id:
                connected.add(edge.source)
        return list(connected)


class ExperimentConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    personas: List[PersonaProfile]
    topic: str
    initial_resources: List[Dict[str, str]] = Field(default_factory=list)
    rounds: int = 20
    max_messages_per_round: int = 3
    metrics: List[str] = Field(default_factory=lambda: [
        "belief_shift", "agreement_network", "deception_signals",
        "influence_centrality", "polarization", "trust_dynamics"
    ])
    created_at: datetime = Field(default_factory=datetime.now)
    config_path: Optional[str] = None


class ExperimentState(BaseModel):
    config: ExperimentConfig
    current_round: int = 0
    messages: List[Message] = Field(default_factory=list)
    network: NetworkGraph = Field(default_factory=NetworkGraph)
    status: Literal["pending", "running", "paused", "completed", "failed"] = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metrics_history: List[Dict[str, Any]] = Field(default_factory=list)


class ResourceShare(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    title: str
    description: str
    shared_by: str  # user or persona id
    shared_at: datetime = Field(default_factory=datetime.now)
    persona_reactions: Dict[str, List[Message]] = Field(default_factory=dict)  # persona_id -> comments
    github_issue_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class ExperimentMetrics(BaseModel):
    experiment_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    round_number: int
    belief_shift: Dict[str, float] = Field(default_factory=dict)
    agreement_matrix: List[List[float]] = Field(default_factory=list)
    deception_indices: Dict[str, float] = Field(default_factory=dict)
    influence_scores: Dict[str, float] = Field(default_factory=dict)
    polarization_index: float = 0.0
    network_modularity: float = 0.0
    avg_trust: float = 0.0
    message_count: int = 0
    unique_interactions: int = 0