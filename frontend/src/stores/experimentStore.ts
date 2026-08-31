import { create } from 'zustand';
import { ExperimentState, ExperimentConfig, Message, ExperimentMetrics, ResourceShare } from '../types';

interface ExperimentStore {
  currentExperiment: ExperimentState | null;
  experiments: ExperimentConfig[];
  messages: Message[];
  resources: ResourceShare[];
  metrics: ExperimentMetrics[];
  
  // Connection status
  isConnected: boolean;
  connectionError: string | null;
  
  // Actions
  setCurrentExperiment: (exp: ExperimentState | null) => void;
  updateExperimentStatus: (status: ExperimentState['status']) => void;
  incrementRound: (round: number) => void;
  addMessage: (message: Message) => void;
  setMessages: (messages: Message[]) => void;
  addResource: (resource: ResourceShare) => void;
  setResources: (resources: ResourceShare[]) => void;
  addMetrics: (metrics: ExperimentMetrics) => void;
  setMetrics: (metrics: ExperimentMetrics[]) => void;
  setExperiments: (experiments: ExperimentConfig[]) => void;
  setConnected: (connected: boolean) => void;
  setConnectionError: (error: string | null) => void;
  reset: () => void;
}

export const useExperimentStore = create<ExperimentStore>((set) => ({
  currentExperiment: null,
  experiments: [],
  messages: [],
  resources: [],
  metrics: [],
  isConnected: false,
  connectionError: null,
  
  setCurrentExperiment: (exp) => set({ currentExperiment: exp }),
  
  updateExperimentStatus: (status) => set((state) => ({
    currentExperiment: state.currentExperiment ? { ...state.currentExperiment, status } : null
  })),
  
  incrementRound: (round) => set((state) => ({
    currentExperiment: state.currentExperiment ? { ...state.currentExperiment, current_round: round } : null
  })),
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message].slice(-500) // Keep last 500
  })),
  
  setMessages: (messages) => set({ messages }),
  
  addResource: (resource) => set((state) => ({
    resources: [...state.resources, resource]
  })),
  
  setResources: (resources) => set({ resources }),
  
  addMetrics: (metrics) => set((state) => ({
    metrics: [...state.metrics, metrics]
  })),
  
  setMetrics: (metrics) => set({ metrics }),
  
  setExperiments: (experiments) => set({ experiments }),
  
  setConnected: (connected) => set({ isConnected: connected }),
  
  setConnectionError: (error) => set({ connectionError: error }),
  
  reset: () => set({
    currentExperiment: null,
    messages: [],
    resources: [],
    metrics: [],
    isConnected: false,
    connectionError: null,
  }),
}));