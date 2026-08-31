import { create } from 'zustand';
import { NetworkData, NetworkNode, NetworkEdge } from '../types';

interface NetworkStore {
  networkData: NetworkData | null;
  layout: 'force' | 'circular' | 'hierarchical';
  selectedNodeId: string | null;
  hoveredNodeId: string | null;
  hoveredEdgeId: string | null;
  filter: {
    minWeight: number;
    showSentiment: boolean;
    showAgreement: boolean;
    genderFilter: 'all' | 'male' | 'female';
  };
  
  // Actions
  setNetworkData: (data: NetworkData) => void;
  updateNode: (id: string, updates: Partial<NetworkNode>) => void;
  updateEdge: (source: string, target: string, updates: Partial<NetworkEdge>) => void;
  setLayout: (layout: 'force' | 'circular' | 'hierarchical') => void;
  setSelectedNode: (id: string | null) => void;
  setHoveredNode: (id: string | null) => void;
  setHoveredEdge: (id: string | null) => void;
  setFilter: (filter: Partial<NetworkStore['filter']>) => void;
  getConnectedNodes: (nodeId: string) => string[];
  getEdgeWeight: (source: string, target: string) => number;
}

export const useNetworkStore = create<NetworkStore>((set, get) => ({
  networkData: null,
  layout: 'force',
  selectedNodeId: null,
  hoveredNodeId: null,
  hoveredEdgeId: null,
  filter: {
    minWeight: 0,
    showSentiment: true,
    showAgreement: true,
    genderFilter: 'all',
  },
  
  setNetworkData: (data) => set({ networkData: data }),
  
  updateNode: (id, updates) => set((state) => ({
    networkData: state.networkData ? {
      ...state.networkData,
      nodes: state.networkData.nodes.map(n => n.id === id ? { ...n, ...updates } : n)
    } : null
  })),
  
  updateEdge: (source, target, updates) => set((state) => ({
    networkData: state.networkData ? {
      ...state.networkData,
      edges: state.networkData.edges.map(e => 
        e.source === source && e.target === target ? { ...e, ...updates } : e
      )
    } : null
  })),
  
  setLayout: (layout) => set({ layout }),
  
  setSelectedNode: (id) => set({ selectedNodeId: id }),
  
  setHoveredNode: (id) => set({ hoveredNodeId: id }),
  
  setHoveredEdge: (id) => set({ hoveredEdgeId: id }),
  
  setFilter: (filter) => set((state) => ({
    filter: { ...state.filter, ...filter }
  })),
  
  getConnectedNodes: (nodeId) => {
    const { networkData } = get();
    if (!networkData) return [];
    
    const connected = new Set<string>();
    networkData.edges.forEach(edge => {
      if (edge.source === nodeId) connected.add(edge.target);
      if (edge.target === nodeId) connected.add(edge.source);
    });
    return Array.from(connected);
  },
  
  getEdgeWeight: (source, target) => {
    const { networkData } = get();
    if (!networkData) return 0;
    const edge = networkData.edges.find(e => e.source === source && e.target === target);
    return edge?.weight ?? 0;
  },
}));