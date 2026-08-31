import { useEffect, useRef, useCallback, useState } from 'react';
import { useExperimentStore } from '../stores/experimentStore';
import { usePersonaStore } from '../stores/personaStore';
import { useNetworkStore } from '../stores/networkStore';
import { Message, NetworkData, ExperimentState, PersonaState, ExperimentMetrics } from '../types';

export function useWebSocket(experimentId: string | null) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  
  const { 
    setCurrentExperiment, 
    updateExperimentStatus, 
    incrementRound, 
    addMessage, 
    setMessages,
    addMetrics,
    setConnected,
    setConnectionError 
  } = useExperimentStore();
  
  const { setPersonas, updatePersona } = usePersonaStore();
  const { setNetworkData } = useNetworkStore();

  const connect = useCallback(() => {
    if (!experimentId) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    
    setIsConnecting(true);
    setConnectionError(null);
    
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/${experimentId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnecting(false);
      setConnected(true);
      setConnectionError(null);
      
      // Request initial state
      ws.send(JSON.stringify({ type: 'get_state' }));
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        handleMessage(msg);
      } catch (e) {
        console.error('Failed to parse WS message:', e);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
      setIsConnecting(false);
      
      // Reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionError('Connection error');
      setIsConnecting(false);
    };
  }, [experimentId, setConnected, setConnectionError]);

  const handleMessage = (msg: any) => {
    switch (msg.type) {
      case 'full_state':
        handleFullState(msg.data);
        break;
      case 'new_message':
        addMessage(msg.data);
        break;
      case 'persona_update':
        updatePersona(msg.data.id, msg.data);
        break;
      case 'network_update':
        setNetworkData(msg.data);
        break;
      case 'experiment_state':
        updateExperimentStatus(msg.data.status);
        if (msg.data.current_round !== undefined) {
          incrementRound(msg.data.current_round);
        }
        if (msg.data.metrics) {
          addMetrics(msg.data.metrics);
        }
        break;
      case 'pong':
        // Heartbeat response
        break;
    }
  };

  const handleFullState = (data: any) => {
    if (data.personas) {
      setPersonas(data.personas);
    }
    if (data.network) {
      setNetworkData(data.network);
    }
    if (data.messages) {
      setMessages(data.messages);
    }
  };

  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  const sendMessage = useCallback((content: string) => {
    send({ type: 'send_message', content });
  }, [send]);

  const shareResource = useCallback((resource: any) => {
    send({ type: 'share_resource', resource });
  }, [send]);

  const sendControl = useCallback((action: string, params?: any) => {
    send({ type: 'control', action, ...params });
  }, [send]);

  useEffect(() => {
    if (experimentId) {
      connect();
    } else {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [experimentId, connect]);

  return {
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
    isConnecting,
    sendMessage,
    shareResource,
    sendControl,
    reconnect: connect,
  };
}