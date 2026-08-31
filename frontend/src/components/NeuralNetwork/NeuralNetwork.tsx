import React, { useRef, useEffect, useCallback, useMemo } from 'react';
import { useNetworkStore } from '../stores/networkStore';
import { usePersonaStore } from '../stores/personaStore';
import { NetworkNode, NetworkEdge, Gender, OCEANTraits } from '../types';
import { clsx } from 'clsx';

interface NeuralNetworkProps {
  width?: number;
  height?: number;
  onNodeClick?: (node: NetworkNode) => void;
  onNodeHover?: (node: NetworkNode | null) => void;
}

export function NeuralNetwork({ 
  width = 800, 
  height = 600, 
  onNodeClick, 
  onNodeHover 
}: NeuralNetworkProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const { 
    networkData, 
    layout, 
    selectedNodeId, 
    hoveredNodeId, 
    filter 
  } = useNetworkStore();
  const { getPersonaSummary } = usePersonaStore();

  // Simulation state
  const positionsRef = useRef<Map<string, { x: number; y: number; vx: number; vy: number }>>(new Map());
  const targetPositionsRef = useRef<Map<string, { x: number; y: number }>>(new Map());

  // Initialize positions
  useEffect(() => {
    if (!networkData || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    networkData.nodes.forEach((node, i) => {
      const existing = positionsRef.current.get(node.id);
      if (!existing) {
        // Initialize in a circle
        const angle = (i / networkData.nodes.length) * Math.PI * 2;
        const radius = Math.min(canvas.width, canvas.height) * 0.35;
        positionsRef.current.set(node.id, {
          x: centerX + Math.cos(angle) * radius,
          y: centerY + Math.sin(angle) * radius,
          vx: 0,
          vy: 0
        });
      }
    });
  }, [networkData]);

  // Force-directed layout simulation
  const simulate = useCallback(() => {
    if (!networkData || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const nodes = networkData.nodes;
    const edges = networkData.edges.filter(e => e.weight >= filter.minWeight);
    const positions = positionsRef.current;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    const k = 0.01; // Repulsion strength
    const springK = 0.05; // Spring strength
    const damping = 0.85;
    const minDist = 50;
    const maxDist = 300;

    // Calculate forces
    const forces = new Map<string, { x: number; y: number }>();
    nodes.forEach(node => forces.set(node.id, { x: 0, y: 0 }));

    // Repulsion between all nodes
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i];
        const b = nodes[j];
        const posA = positions.get(a.id);
        const posB = positions.get(b.id);
        if (!posA || !posB) continue;
        
        const dx = posA.x - posB.x;
        const dy = posA.y - posB.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        
        if (dist < maxDist) {
          const force = (k * minDist * minDist) / (dist * dist);
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;
          
          const forceA = forces.get(a.id)!;
          const forceB = forces.get(b.id)!;
          forceA.x += fx;
          forceA.y += fy;
          forceB.x -= fx;
          forceB.y -= fy;
        }
      }
    }

    // Spring attraction for connected nodes
    edges.forEach(edge => {
      const posA = positions.get(edge.source);
      const posB = positions.get(edge.target);
      if (!posA || !posB) return;
      
      const dx = posB.x - posA.x;
      const dy = posB.y - posA.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      
      const targetDist = 100 + (1 - edge.weight) * 150;
      const force = springK * (dist - targetDist);
      const fx = (dx / dist) * force * edge.weight;
      const fy = (dy / dist) * force * edge.weight;
      
      const forceA = forces.get(edge.source)!;
      const forceB = forces.get(edge.target)!;
      forceA.x += fx;
      forceA.y += fy;
      forceB.x -= fx;
      forceB.y -= fy;
    });

    // Center attraction
    nodes.forEach(node => {
      const pos = positions.get(node.id);
      if (!pos) return;
      
      const dx = centerX - pos.x;
      const dy = centerY - pos.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist > 1) {
        const force = 0.001 * dist;
        const forceObj = forces.get(node.id)!;
        forceObj.x += (dx / dist) * force;
        forceObj.y += (dy / dist) * force;
      }
    });

    // Apply forces
    positions.forEach((pos, id) => {
      const force = forces.get(id);
      if (!force) return;
      
      pos.vx = (pos.vx + force.x) * damping;
      pos.vy = (pos.vy + force.y) * damping;
      
      // Limit velocity
      const maxVel = 10;
      const vel = Math.sqrt(pos.vx * pos.vx + pos.vy * pos.vy);
      if (vel > maxVel) {
        pos.vx = (pos.vx / vel) * maxVel;
        pos.vy = (pos.vy / vel) * maxVel;
      }
      
      pos.x += pos.vx;
      pos.y += pos.vy;
      
      // Keep in bounds with padding
      const padding = 60;
      pos.x = Math.max(padding, Math.min(canvas.width - padding, pos.x));
      pos.y = Math.max(padding, Math.min(canvas.height - padding, pos.y));
    });
  }, [networkData, filter.minWeight]);

  // Render loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d')!;
    let lastTime = 0;
    
    const render = (time: number) => {
      // Simulate at 60fps max
      if (time - lastTime > 16) {
        simulate();
        lastTime = time;
      }
      
      draw(ctx);
      animationRef.current = requestAnimationFrame(render);
    };
    
    animationRef.current = requestAnimationFrame(render);
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [simulate]);

  const draw = useCallback((ctx: CanvasRenderingContext2D) => {
    if (!networkData || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const { nodes, edges } = networkData;
    const positions = positionsRef.current;
    
    // Clear
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw background grid (subtle)
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 0.5;
    const gridSize = 50;
    for (let x = 0; x <= canvas.width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y <= canvas.height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }
    
    // Filter edges
    const visibleEdges = edges.filter(e => e.weight >= filter.minWeight);
    
    // Draw edges
    visibleEdges.forEach(edge => {
      const posA = positions.get(edge.source);
      const posB = positions.get(edge.target);
      if (!posA || !posB) return;
      
      const isHovered = hoveredNodeId && (edge.source === hoveredNodeId || edge.target === hoveredNodeId);
      const isSelected = selectedNodeId && (edge.source === selectedNodeId || edge.target === selectedNodeId);
      
      // Edge color based on sentiment/agreement
      let strokeColor: string;
      let opacity = 0.3 + edge.weight * 0.4;
      
      if (filter.showSentiment) {
        // Red to green based on sentiment
        const hue = 120 * (edge.avg_sentiment + 1) / 2; // 0=red, 120=green
        strokeColor = `hsl(${hue}, 70%, 50%)`;
      } else if (filter.showAgreement) {
        // Blue to purple based on agreement
        const hue = 220 + edge.agreement_score * 60;
        strokeColor = `hsl(${hue}, 70%, 50%)`;
      } else {
        strokeColor = '#64748b';
      }
      
      if (isHovered || isSelected) {
        opacity = 0.8;
      }
      
      ctx.beginPath();
      ctx.moveTo(posA.x, posA.y);
      
      // Curved edges for bidirectional
      const reverseEdge = edges.find(e => e.source === edge.target && e.target === edge.source);
      if (reverseEdge) {
        const midX = (posA.x + posB.x) / 2;
        const midY = (posA.y + posB.y) / 2;
        const dx = posB.x - posA.x;
        const dy = posB.y - posA.y;
        const perpX = -dy * 0.3;
        const perpY = dx * 0.3;
        ctx.quadraticCurveTo(midX + perpX, midY + perpY, posB.x, posB.y);
      } else {
        ctx.lineTo(posB.x, posB.y);
      }
      
      ctx.strokeStyle = strokeColor;
      ctx.globalAlpha = opacity;
      ctx.lineWidth = 1 + edge.weight * 3;
      ctx.stroke();
      ctx.globalAlpha = 1;
      
      // Arrowhead for directed edges
      if (!reverseEdge) {
        drawArrowhead(ctx, posA.x, posA.y, posB.x, posB.y, strokeColor, opacity);
      }
    });
    
    // Draw nodes
    nodes.forEach(node => {
      const pos = positions.get(node.id);
      if (!pos) return;
      
      const isSelected = node.id === selectedNodeId;
      const isHovered = node.id === hoveredNodeId;
      const persona = getPersonaSummary(node.id);
      
      const radius = 16 + Math.min(node.message_count * 1.5, 24);
      const pulseScale = isHovered ? 1.15 : isSelected ? 1.1 : 1;
      
      // Node glow
      if (isSelected || isHovered) {
        const glowColor = node.gender === 'female' ? '#ec4899' : '#3b82f6';
        const gradient = ctx.createRadialGradient(
          pos.x, pos.y, radius * 0.5,
          pos.x, pos.y, radius * 2.5
        );
        gradient.addColorStop(0, `${glowColor}40`);
        gradient.addColorStop(1, `${glowColor}00`);
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, radius * 2.5, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
      }
      
      // Node circle
      const nodeColor = node.gender === 'female' ? '#ec4899' : '#3b82f6';
      const borderColor = isSelected ? '#fff' : (isHovered ? '#fff' : nodeColor);
      const borderWidth = isSelected ? 3 : (isHovered ? 2 : 1.5);
      
      // Model indicator (local vs gemini)
      const isLocal = node.assigned_model === 'local';
      
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, radius * pulseScale, 0, Math.PI * 2);
      
      // Gradient fill
      const gradient = ctx.createRadialGradient(
        pos.x - radius * 0.3, pos.y - radius * 0.3, 0,
        pos.x, pos.y, radius
      );
      gradient.addColorStop(0, lightenColor(nodeColor, 30));
      gradient.addColorStop(1, nodeColor);
      ctx.fillStyle = gradient;
      ctx.fill();
      
      // Border
      ctx.strokeStyle = borderColor;
      ctx.lineWidth = borderWidth;
      ctx.stroke();
      
      // Local model indicator
      if (isLocal) {
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, radius * pulseScale + 4, 0, Math.PI * 2);
        ctx.strokeStyle = '#10b981';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([4, 4]);
        ctx.stroke();
        ctx.setLineDash([]);
      }
      
      // Emotional valence indicator (inner ring)
      const valence = node.emotional_valence;
      if (Math.abs(valence) > 0.1) {
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, radius * 0.5, 0, Math.PI * 2);
        const valenceColor = valence > 0 ? '#10b981' : '#ef4444';
        ctx.fillStyle = `${valenceColor}${Math.floor(Math.abs(valence) * 100).toString(16).padStart(2, '0')}`;
        ctx.fill();
      }
      
      // Label
      if (radius > 18 || isHovered || isSelected) {
        ctx.font = `500 ${isHovered || isSelected ? 13 : 11}px Inter, sans-serif`;
        ctx.fillStyle = '#f8fafc';
        ctx.textAlign = 'center';
        ctx.fillText(node.name, pos.x, pos.y - radius - 8);
        
        // Message count
        if (node.message_count > 0) {
          ctx.font = `400 10px Inter, sans-serif`;
          ctx.fillStyle = '#94a3b8';
          ctx.fillText(`${node.message_count} msgs`, pos.x, pos.y - radius + 16);
        }
      }
    });
  }, [networkData, selectedNodeId, hoveredNodeId, filter, getPersonaSummary]);

  const drawArrowhead = (
    ctx: CanvasRenderingContext2D,
    fromX: number, fromY: number,
    toX: number, toY: number,
    color: string, opacity: number
  ) => {
    const headLen = 8;
    const angle = Math.atan2(toY - fromY, toX - fromX);
    const x = toX - headLen * Math.cos(angle);
    const y = toY - headLen * Math.sin(angle);
    
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(
      x + headLen * Math.cos(angle - Math.PI / 6),
      y + headLen * Math.sin(angle - Math.PI / 6)
    );
    ctx.lineTo(
      x + headLen * Math.cos(angle + Math.PI / 6),
      y + headLen * Math.sin(angle + Math.PI / 6)
    );
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.globalAlpha = opacity;
    ctx.fill();
    ctx.globalAlpha = 1;
  };

  const lightenColor = (color: string, percent: number) => {
    const num = parseInt(color.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent);
    const R = Math.min(255, (num >> 16) + amt);
    const G = Math.min(255, ((num >> 8) & 0x00FF) + amt);
    const B = Math.min(255, (num & 0x0000FF) + amt);
    return `#${(0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1)}`;
  };

  // Mouse interaction
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!networkData || !canvasRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const positions = positionsRef.current;
    
    let hovered: string | null = null;
    let minDist = Infinity;
    
    networkData.nodes.forEach(node => {
      const pos = positions.get(node.id);
      if (!pos) return;
      
      const radius = 16 + Math.min(node.message_count * 1.5, 24);
      const dx = pos.x - mouseX;
      const dy = pos.y - mouseY;
      const dist = Math.sqrt(dx * dx + dy * dy);
      
      if (dist < radius + 8 && dist < minDist) {
        minDist = dist;
        hovered = node.id;
      }
    });
    
    useNetworkStore.getState().setHoveredNode(hovered);
    if (onNodeHover) {
      const persona = hovered ? getPersonaSummary(hovered) : null;
      onNodeHover(persona ? { 
        id: persona.id, 
        name: persona.name, 
        gender: persona.gender, 
        avatar_seed: persona.avatar_seed,
        message_count: persona.message_count,
        emotional_valence: persona.emotional_valence,
        arousal: persona.arousal,
        assigned_model: persona.assigned_model,
        traits: persona.ocean_traits
      } : null);
    }
  }, [networkData, onNodeHover]);

  const handleClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!networkData || !canvasRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const positions = positionsRef.current;
    
    networkData.nodes.forEach(node => {
      const pos = positions.get(node.id);
      if (!pos) return;
      
      const radius = 16 + Math.min(node.message_count * 1.5, 24);
      const dx = pos.x - mouseX;
      const dy = pos.y - mouseY;
      const dist = Math.sqrt(dx * dx + dy * dy);
      
      if (dist < radius + 8) {
        useNetworkStore.getState().setSelectedNode(node.id);
        if (onNodeClick) {
          const persona = getPersonaSummary(node.id);
          if (persona) {
            onNodeClick({
              id: persona.id,
              name: persona.name,
              gender: persona.gender,
              avatar_seed: persona.avatar_seed,
              message_count: persona.message_count,
              emotional_valence: persona.emotional_valence,
              arousal: persona.arousal,
              assigned_model: persona.assigned_model,
              traits: persona.ocean_traits
            });
          }
        }
      }
    });
  }, [networkData, onNodeClick, getPersonaSummary]);

  const handleDoubleClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    // Reset view on double-click empty space
    const rect = canvasRef.current!.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    let hitNode = false;
    if (networkData) {
      const positions = positionsRef.current;
      networkData.nodes.forEach(node => {
        const pos = positions.get(node.id);
        if (!pos) return;
        const radius = 16 + Math.min(node.message_count * 1.5, 24);
        const dx = pos.x - mouseX;
        const dy = pos.y - mouseY;
        if (Math.sqrt(dx * dx + dy * dy) < radius + 8) {
          hitNode = true;
        }
      });
    }
    
    if (!hitNode) {
      useNetworkStore.getState().setSelectedNode(null);
    }
  }, [networkData]);

  return (
    <div className="relative w-full h-full">
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="w-full h-full block cursor-crosshair"
        onMouseMove={handleMouseMove}
        onClick={handleClick}
        onDoubleClick={handleDoubleClick}
        style={{ 
          background: 'radial-gradient(ellipse at center, #0f172a 0%, #020617 100%)',
          borderRadius: '12px'
        }}
      />
      
      {/* Legend */}
      <div className="absolute bottom-4 left-4 right-4 flex flex-wrap gap-4 justify-center text-xs text-dark-400 bg-dark-900/80 backdrop-blur rounded-lg p-3 border border-dark-700">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-pink-500"></div>
          <span>Female</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-500"></div>
          <span>Male</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full border-2 border-green-500"></div>
          <span>Local Model</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-1 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 rounded"></div>
          <span>Sentiment</span>
        </div>
      </div>
    </div>
  );
}