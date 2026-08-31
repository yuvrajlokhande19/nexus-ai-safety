import React, { useState } from 'react';
import { useExperimentStore } from '../stores/experimentStore';
import { usePersonaStore } from '../stores/personaStore';
import { ExperimentConfig, OCEANTraits, Gender } from '../types';
import { clsx } from 'clsx';
import {
  Play, Pause, Stop, RotateCcw, Plus, Minus,
  Settings, Download, Upload, FileText,
  ChevronDown, ChevronUp, Brain, Users,
  Zap, Sparkles, TrendingUp
} from 'lucide-react';

interface ExperimentControlProps {
  onCreateExperiment: () => void;
}

export function ExperimentControl({ onCreateExperiment }: ExperimentControlProps) {
  const { 
    currentExperiment, 
    experiments, 
    metrics,
    isConnected,
    start_experiment,
    pause_experiment,
    resume_experiment,
    stop_experiment,
    updateExperimentStatus,
    incrementRound
  } = useExperimentStore();
  
  const { getAllPersonas } = usePersonaStore();
  
  const [showConfig, setShowConfig] = useState(false);
  const [configForm, setConfigForm] = useState({
    name: '',
    description: '',
    topic: '',
    persona_count: 5,
    local_persona_count: 1,
    rounds: 20,
  });
  const [selectedExperimentId, setSelectedExperimentId] = useState<string | null>(null);
  const [showExperimentsList, setShowExperimentsList] = useState(false);

  const handleCreateExperiment = async (e: React.FormEvent) => {
    e.preventDefault();
    // This would call the API
    console.log('Create experiment:', configForm);
    onCreateExperiment();
    setShowConfig(false);
  };

  const handleStart = () => {
    if (currentExperiment) {
      // API call would go here
      updateExperimentStatus('running');
    }
  };

  const handlePause = () => {
    if (currentExperiment) {
      updateExperimentStatus('paused');
    }
  };

  const handleResume = () => {
    if (currentExperiment) {
      updateExperimentStatus('running');
    }
  };

  const handleStop = () => {
    if (currentExperiment) {
      updateExperimentStatus('completed');
    }
  };

  const statusColors: Record<string, string> = {
    pending: 'text-yellow-400 bg-yellow-500/20',
    running: 'text-green-400 bg-green-500/20',
    paused: 'text-blue-400 bg-blue-500/20',
    completed: 'text-purple-400 bg-purple-500/20',
    failed: 'text-red-400 bg-red-500/20',
  };

  const statusIcons: Record<string, React.ReactNode> = {
    pending: <Settings className="w-4 h-4" />,
    running: <Play className="w-4 h-4" />,
    paused: <Pause className="w-4 h-4" />,
    completed: <FileText className="w-4 h-4" />,
    failed: <RotateCcw className="w-4 h-4" />,
  };

  if (!currentExperiment && experiments.length === 0) {
    return (
      <div className="card h-full flex flex-col">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-dark-100 flex items-center gap-2">
            <Brain className="w-5 h-5 text-primary-400" />
            Experiment Control
          </h2>
          <span className={clsx('px-2 py-1 rounded-full text-xs font-medium', statusColors.pending)}>
            <Settings className="w-3 h-3 mr-1" /> No Experiment
          </span>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          <button 
            onClick={() => setShowConfig(true)}
            className="btn-primary w-full max-w-md py-8 flex flex-col items-center gap-3"
          >
            <Plus className="w-12 h-12 text-primary-400" />
            <span className="text-lg font-medium">Create New Experiment</span>
            <p className="text-dark-500 text-sm text-center">
              Configure personas, topic, and rounds to begin
            </p>
          </button>
        </div>
        
        {showConfig && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <div className="w-full max-w-md bg-dark-900 rounded-2xl border border-dark-700 p-6 animate-in max-h-[90vh] overflow-y-auto">
              <h3 className="text-xl font-semibold mb-6">Create Experiment</h3>
              <form onSubmit={handleCreateExperiment} className="space-y-4">
                <div>
                  <label className="block text-sm text-dark-400 mb-1">Experiment Name</label>
                  <input 
                    type="text" 
                    className="input"
                    value={configForm.name}
                    onChange={(e) => setConfigForm({...configForm, name: e.target.value})}
                    placeholder="e.g., Deception Detection Study"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm text-dark-400 mb-1">Description</label>
                  <textarea 
                    className="input"
                    value={configForm.description}
                    onChange={(e) => setConfigForm({...configForm, description: e.target.value})}
                    rows={3}
                    placeholder="What is this experiment studying?"
                  />
                </div>
                <div>
                  <label className="block text-sm text-dark-400 mb-1">Discussion Topic</label>
                  <input 
                    type="text" 
                    className="input"
                    value={configForm.topic}
                    onChange={(e) => setConfigForm({...configForm, topic: e.target.value})}
                    placeholder="e.g., AI consciousness, climate policy, social media regulation"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-dark-400 mb-1">Personas</label>
                    <select 
                      className="input"
                      value={configForm.persona_count}
                      onChange={(e) => setConfigForm({...configForm, persona_count: parseInt(e.target.value)})}
                    >
                      {[3,4,5,6,7,8,9,10,12,15].map(n => (
                        <option key={n} value={n}>{n}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-dark-400 mb-1">Local (Gemma)</label>
                    <select 
                      className="input"
                      value={configForm.local_persona_count}
                      onChange={(e) => setConfigForm({...configForm, local_persona_count: parseInt(e.target.value)})}
                    >
                      {[0,1,2].map(n => (
                        <option key={n} value={n}>{n}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm text-dark-400 mb-1">Rounds</label>
                  <select 
                    className="input"
                    value={configForm.rounds}
                    onChange={(e) => setConfigForm({...configForm, rounds: parseInt(e.target.value)})}
                  >
                    {[10,15,20,30,50].map(n => (
                      <option key={n} value={n}>{n}</option>
                    ))}
                  </select>
                </div>
                <div className="flex gap-3 pt-4">
                  <button type="button" onClick={() => setShowConfig(false)} className="btn-secondary flex-1">Cancel</button>
                  <button type="submit" className="btn-primary flex-1">Create & Start</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    );
  }

  const exp = currentExperiment || experiments.find(e => e.id === selectedExperimentId);
  const personas = getAllPersonas();
  const activePersonas = personas.filter(p => p.is_active);
  const localCount = personas.filter(p => p.profile.assigned_model === 'local').length;
  const geminiCount = personas.filter(p => p.profile.assigned_model === 'gemini').length;

  return (
    <div className="card h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-dark-100 flex items-center gap-2">
          <Brain className="w-5 h-5 text-primary-400" />
          Experiment Control
        </h2>
        {exp && (
          <span className={clsx('px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1', statusColors[exp.status])}>
            {statusIcons[exp.status]}
            {exp.status.charAt(0).toUpperCase() + exp.status.slice(1)}
          </span>
        )}
      </div>

      {exp && (
        <>
          {/* Experiment Info */}
          <div className="mb-4 space-y-2">
            <h3 className="font-medium text-dark-100">{exp.config?.name || exp.name}</h3>
            <p className="text-sm text-dark-500 line-clamp-2">{exp.config?.description || exp.description}</p>
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="badge-primary">{exp.config?.topic || exp.topic}</span>
              <span className="badge">Round {exp.current_round}/{exp.config?.rounds || exp.rounds}</span>
              <span className="badge">{personas.length} personas</span>
              <span className="badge-success">{localCount} local</span>
              <span className="badge">{geminiCount} Gemini</span>
            </div>
          </div>

          {/* Progress */}
          <div className="mb-4">
            <div className="flex justify-between text-xs text-dark-500 mb-1">
              <span>Progress</span>
              <span>{Math.round((exp.current_round / (exp.config?.rounds || exp.rounds)) * 100)}%</span>
            </div>
            <div className="h-2 bg-dark-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full transition-all duration-500"
                style={{ width: `${(exp.current_round / (exp.config?.rounds || exp.rounds)) * 100}%` }}
              />
            </div>
          </div>

          {/* Controls */}
          <div className="flex gap-2 mb-4">
            {exp.status === 'pending' && (
              <button onClick={handleStart} className="btn-primary flex-1 flex items-center justify-center gap-2">
                <Play className="w-4 h-4" /> Start
              </button>
            )}
            {exp.status === 'running' && (
              <button onClick={handlePause} className="btn-secondary flex-1 flex items-center justify-center gap-2">
                <Pause className="w-4 h-4" /> Pause
              </button>
            )}
            {exp.status === 'paused' && (
              <button onClick={handleResume} className="btn-primary flex-1 flex items-center justify-center gap-2">
                <Play className="w-4 h-4" /> Resume
              </button>
            )}
            {(exp.status === 'running' || exp.status === 'paused') && (
              <button onClick={handleStop} className="btn-danger flex-1 flex items-center justify-center gap-2">
                <Stop className="w-4 h-4" /> Stop
              </button>
            )}
            {exp.status === 'completed' && (
              <button className="btn-secondary flex-1 flex items-center justify-center gap-2">
                <Download className="w-4 h-4" /> Report
              </button>
            )}
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-3 gap-2 mb-4">
            <div className="bg-dark-800/50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-primary-400">{metrics.length > 0 ? metrics[metrics.length - 1].message_count : 0}</div>
              <div className="text-xs text-dark-500">Messages</div>
            </div>
            <div className="bg-dark-800/50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-green-400">{metrics.length > 0 ? metrics[metrics.length - 1].unique_interactions : 0}</div>
              <div className="text-xs text-dark-500">Interactions</div>
            </div>
            <div className="bg-dark-800/50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-blue-400">{metrics.length > 0 ? (metrics[metrics.length - 1].avg_trust * 100).toFixed(0) : 0}%</div>
              <div className="text-xs text-dark-500">Avg Trust</div>
            </div>
          </div>

          {/* Current Metrics */}
          {metrics.length > 0 && (
            <div className="flex-1 overflow-y-auto space-y-3 border-t border-dark-700 pt-4">
              <h4 className="font-medium text-dark-100 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-green-400" />
                Live Metrics
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between p-2 bg-dark-800/50 rounded">
                  <span className="text-dark-400">Polarization</span>
                  <span className="font-medium text-white">
                    {(metrics[metrics.length - 1].polarization_index * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between p-2 bg-dark-800/50 rounded">
                  <span className="text-dark-400">Network Modularity</span>
                  <span className="font-medium text-white">
                    {(metrics[metrics.length - 1].network_modularity * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between p-2 bg-dark-800/50 rounded">
                  <span className="text-dark-400">Avg Trust</span>
                  <span className="font-medium text-white">
                    {(metrics[metrics.length - 1].avg_trust * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Experiments List */}
      {experiments.length > 0 && (
        <div className="border-t border-dark-700 pt-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-dark-100 flex items-center gap-2">
              <FileText className="w-4 h-4 text-dark-400" />
              Saved Experiments
            </h4>
            <button 
              onClick={() => setShowExperimentsList(!showExperimentsList)}
              className="text-dark-400 hover:text-dark-100"
            >
              {showExperimentsList ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          </div>
          
          {showExperimentsList && (
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {experiments.map(exp => (
                <button
                  key={exp.id}
                  onClick={() => setSelectedExperimentId(exp.id)}
                  className={clsx(
                    'w-full text-left p-3 rounded-lg transition-colors',
                    selectedExperimentId === exp.id 
                      ? 'bg-primary-500/20 border border-primary-500/30' 
                      : 'bg-dark-800/50 hover:bg-dark-800'
                  )}
                >
                  <div className="font-medium text-dark-100">{exp.name}</div>
                  <div className="text-xs text-dark-500 flex gap-3 mt-1">
                    <span>{exp.personas?.length || 0} personas</span>
                    <span>{exp.rounds} rounds</span>
                    <span>{exp.topic}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}