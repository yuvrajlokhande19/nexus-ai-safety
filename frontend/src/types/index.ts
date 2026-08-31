export interface OCEANTraits {
  openness: number;
  conscientiousness: number;
  extraversion: number;
  agreeableness: number;
  neuroticism: number;
}

export type Gender = 'male' | 'female' | 'non_binary';

export interface PersonaProfile {
  id: string;
  name: string;
  age: number;
  gender: Gender;
  background: string;
  speaking_style: string;
  values: string[];
  biases: string[];
  ocean_traits: OCEANTraits;
  avatar_seed: string;
  assigned_model: 'local' | 'gemini';
  model_config: Record<string, any>;
}

export interface CognitiveState {
  current_beliefs: Record<string, number>;
  emotional_valence: number;
  arousal: number;
  trust_levels: Record<string, number>;
  attention_focus: string | null;
  private_thoughts: string[];
}

export interface PersonaState {
  profile: PersonaProfile;
  cognitive: CognitiveState;
  message_count: number;
  last_active: string;
  is_active: boolean;
}

export type MessageType = 
  | 'chat' 
  | 'system' 
  | 'resource_share' 
  | 'comment' 
  | 'reaction' 
  | 'private_thought' 
  | 'belief_update';

export interface Message {
  id: string;
  type: MessageType;
  sender_id: string;
  sender_name: string;
  content: string;
  timestamp: string;
  target_ids: string[];
  metadata: Record<string, any>;
  resource_url?: string;
  resource_title?: string;
  parent_message_id?: string;
  reaction_type?: string;
  sentiment?: number;
}

export interface NetworkEdge {
  source: string;
  target: string;
  weight: number;
  interaction_count: number;
  avg_sentiment: number;
  agreement_score: number;
  last_interaction: string;
}

export interface NetworkGraph {
  nodes: Record<string, PersonaState>;
  edges: Record<string, NetworkEdge>;
}

export interface ExperimentConfig {
  id: string;
  name: string;
  description: string;
  personas: PersonaProfile[];
  topic: string;
  initial_resources: ResourceData[];
  rounds: number;
  max_messages_per_round: number;
  metrics: string[];
  created_at: string;
  config_path?: string;
}

export interface ResourceData {
  url: string;
  title: string;
  description: string;
}

export interface ExperimentState {
  config: ExperimentConfig;
  current_round: number;
  messages: Message[];
  network: NetworkGraph;
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed';
  started_at: string | null;
  completed_at: string | null;
  metrics_history: ExperimentMetrics[];
}

export interface ExperimentMetrics {
  experiment_id: string;
  timestamp: string;
  round_number: number;
  belief_shift: Record<string, number>;
  agreement_matrix: number[][];
  deception_indices: Record<string, number>;
  influence_scores: Record<string, number>;
  polarization_index: number;
  network_modularity: number;
  avg_trust: number;
  message_count: number;
  unique_interactions: number;
}

export interface ResourceShare {
  id: string;
  url: string;
  title: string;
  description: string;
  shared_by: string;
  shared_at: string;
  persona_reactions: Record<string, Message[]>;
  github_issue_url?: string;
  tags: string[];
}

export interface NetworkData {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
}

export interface NetworkNode {
  id: string;
  name: string;
  gender: Gender;
  avatar_seed: string;
  message_count: number;
  emotional_valence: number;
  arousal: number;
  assigned_model: 'local' | 'gemini';
  traits: OCEANTraits;
}

export interface WSMessage {
  type: string;
  data: any;
}