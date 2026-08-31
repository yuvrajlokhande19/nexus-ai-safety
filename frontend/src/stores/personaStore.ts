import { create } from 'zustand';
import { PersonaState, PersonaProfile, OCEANTraits, Gender } from '../types';

interface PersonaStore {
  personas: Record<string, PersonaState>;
  selectedPersonaId: string | null;
  
  // Actions
  setPersonas: (personas: Record<string, PersonaState>) => void;
  updatePersona: (id: string, updates: Partial<PersonaState>) => void;
  setSelectedPersona: (id: string | null) => void;
  getPersona: (id: string) => PersonaState | undefined;
  getAllPersonas: () => PersonaState[];
  getPersonaSummary: (id: string) => PersonaSummary | null;
}

export interface PersonaSummary {
  id: string;
  name: string;
  age: number;
  gender: Gender;
  avatar_seed: string;
  ocean_traits: OCEANTraits;
  message_count: number;
  emotional_valence: number;
  arousal: number;
  is_active: boolean;
  assigned_model: 'local' | 'gemini';
  beliefs: Record<string, number>;
  trust_levels: Record<string, number>;
}

export const usePersonaStore = create<PersonaStore>((set, get) => ({
  personas: {},
  selectedPersonaId: null,
  
  setPersonas: (personas) => set({ personas }),
  
  updatePersona: (id, updates) => set((state) => ({
    personas: {
      ...state.personas,
      [id]: { ...state.personas[id], ...updates }
    }
  })),
  
  setSelectedPersona: (id) => set({ selectedPersonaId: id }),
  
  getPersona: (id) => get().personas[id],
  
  getAllPersonas: () => Object.values(get().personas),
  
  getPersonaSummary: (id) => {
    const persona = get().personas[id];
    if (!persona) return null;
    
    return {
      id: persona.profile.id,
      name: persona.profile.name,
      age: persona.profile.age,
      gender: persona.profile.gender,
      avatar_seed: persona.profile.avatar_seed,
      ocean_traits: persona.profile.ocean_traits,
      message_count: persona.message_count,
      emotional_valence: persona.cognitive.emotional_valence,
      arousal: persona.cognitive.arousal,
      is_active: persona.is_active,
      assigned_model: persona.profile.assigned_model,
      beliefs: persona.cognitive.current_beliefs,
      trust_levels: persona.cognitive.trust_levels,
    };
  },
}));