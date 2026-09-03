import React, { useState } from 'react';
import { usePersonaStore } from '@/stores/personaStore';
import { PersonaSummary, OCEANTraits, Gender } from '../types';
import { clsx } from 'clsx';
import { 
  Brain, Heart, MessageSquare, Users, 
  TrendingUp, TrendingDown, Activity,
  ChevronDown, ChevronUp, Zap, Sparkles
} from 'lucide-react';

interface PersonaPanelProps {
  persona: PersonaSummary | null;
  onClose: () => void;
}

const traitLabels: Record<keyof OCEANTraits, { label: string; icon: React.ReactNode; color: string }> = {
  openness: { label: 'Openness', icon: <Sparkles className="w-4 h-4" />, color: 'text-purple-400' },
  conscientiousness: { label: 'Conscientiousness', icon: <TrendingUp className="w-4 h-4" />, color: 'text-green-400' },
  extraversion: { label: 'Extraversion', icon: <Activity className="w-4 h-4" />, color: 'text-orange-400' },
  agreeableness: { label: 'Agreeableness', icon: <Heart className="w-4 h-4" />, color: 'text-pink-400' },
  neuroticism: { label: 'Neuroticism', icon: <TrendingDown className="w-4 h-4" />, color: 'text-red-400' },
};

const traitDescriptions: Record<keyof OCEANTraits, { high: string; low: string }> = {
  openness: { high: 'Curious, creative, open to new experiences', low: 'Practical, conventional, prefers routine' },
  conscientiousness: { high: 'Organized, disciplined, achievement-oriented', low: 'Spontaneous, flexible, less structured' },
  extraversion: { high: 'Outgoing, energetic, seeks stimulation', low: 'Reserved, solitary, needs less stimulation' },
  agreeableness: { high: 'Cooperative, trusting, compassionate', low: 'Competitive, skeptical, critical' },
  neuroticism: { high: 'Sensitive, anxious, emotionally reactive', low: 'Stable, calm, resilient' },
};

export function PersonaPanel({ persona, onClose }: PersonaPanelProps) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    traits: true,
    beliefs: true,
    trust: true,
    private: false,
  });

  if (!persona) return null;

  const genderColor = persona.gender === 'female' ? 'text-pink-400' : 'text-blue-400';
  const genderIcon = persona.gender === 'female' ? '♀' : '♂';
  
  const valenceColor = persona.emotional_valence > 0.2 ? 'text-green-400' : 
                       persona.emotional_valence < -0.2 ? 'text-red-400' : 'text-yellow-400';
  const valenceLabel = persona.emotional_valence > 0.2 ? 'Positive' : 
                       persona.emotional_valence < -0.2 ? 'Negative' : 'Neutral';

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-2xl max-h-[90vh] bg-dark-900 rounded-2xl border border-dark-700 overflow-hidden flex flex-col animate-in">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-700 bg-dark-950">
          <div className="flex items-center gap-4">
            <div className={clsx(
              'w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-bold text-white',
              persona.gender === 'female' ? 'bg-gradient-to-br from-pink-500 to-purple-600' : 'bg-gradient-to-br from-blue-500 to-indigo-600'
            )}>
              {persona.name.charAt(0)}
            </div>
            <div>
              <h2 className="text-xl font-semibold text-dark-50">{persona.name}</h2>
              <div className="flex items-center gap-3 text-sm text-dark-400 mt-1">
                <span className={clsx('flex items-center gap-1', genderColor)}>
                  {genderIcon} {persona.age}
                </span>
                <span className="flex items-center gap-1">
                  <MessageSquare className="w-4 h-4" /> {persona.message_count} messages
                </span>
                <span className={clsx('flex items-center gap-1 px-2 py-0.5 rounded-full text-xs', 
                  persona.assigned_model === 'local' ? 'bg-green-500/20 text-green-400' : 'bg-purple-500/20 text-purple-400'
                )}>
                  <Zap className="w-3 h-3" /> {persona.assigned_model === 'local' ? 'Local (Gemma)' : 'Gemini API'}
                </span>
              </div>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 rounded-lg text-dark-400 hover:text-dark-100 hover:bg-dark-800 transition-colors"
            aria-label="Close panel"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {/* Emotional State */}
          <div className="card">
            <h3 className="font-medium text-dark-100 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary-400" />
              Emotional State
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-dark-500 uppercase tracking-wider">Valence</label>
                <div className="mt-1 flex items-center gap-3">
                  <div className="flex-1 h-2 bg-dark-800 rounded-full overflow-hidden">
                    <div 
                      className={clsx('h-full rounded-full transition-all duration-500', valenceColor.replace('text', 'bg'))}
                      style={{ width: `${((persona.emotional_valence + 1) / 2) * 100}%` }}
                    />
                  </div>
                  <span className={clsx('text-sm font-medium', valenceColor)}>{valenceLabel}</span>
                </div>
                <p className="text-xs text-dark-500 mt-1">
                  {persona.emotional_valence > 0.2 ? 'Feeling good, optimistic' : 
                   persona.emotional_valence < -0.2 ? 'Feeling down, pessimistic' : 'Neutral mood'}
                </p>
              </div>
              <div>
                <label className="text-xs text-dark-500 uppercase tracking-wider">Arousal</label>
                <div className="mt-1 flex items-center gap-3">
                  <div className="flex-1 h-2 bg-dark-800 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-500 rounded-full transition-all duration-500"
                      style={{ width: `${persona.arousal * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-blue-400">{Math.round(persona.arousal * 100)}%</span>
                </div>
                <p className="text-xs text-dark-500 mt-1">
                  {persona.arousal > 0.7 ? 'High energy, excited' : 
                   persona.arousal < 0.3 ? 'Low energy, calm' : 'Moderate energy'}
                </p>
              </div>
            </div>
          </div>

          {/* OCEAN Traits */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-dark-100 flex items-center gap-2">
                <Brain className="w-5 h-5 text-primary-400" />
                Personality (Big Five)
              </h3>
              <button
                onClick={() => toggleSection('traits')}
                className="text-dark-400 hover:text-dark-100 text-sm"
              >
                {expandedSections.traits ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
            </div>
            
            {expandedSections.traits && (
              <div className="space-y-3" style={{ animation: 'animateIn 0.2s ease-out' }}>
                {(Object.keys(traitLabels) as Array<keyof OCEANTraits>).map(trait => {
                  const value = persona.ocean_traits[trait];
                  const { label, icon, color } = traitLabels[trait];
                  const { high, low } = traitDescriptions[trait];
                  const isHigh = value > 0.6;
                  const isLow = value < 0.4;
                  
                  return (
                    <div key={trait} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className={clsx('w-8 h-8 rounded-lg flex items-center justify-center', color.replace('text', 'bg/20'))}>
                            {icon}
                          </span>
                          <span className="font-medium text-dark-100">{label}</span>
                        </div>
                        <span className={clsx('text-sm font-bold', color)}>{Math.round(value * 100)}%</span>
                      </div>
                      <div className="h-2 bg-dark-800 rounded-full overflow-hidden">
                        <div 
                          className={clsx('h-full rounded-full transition-all duration-500', color.replace('text', 'bg'))}
                          style={{ width: `${value * 100}%` }}
                        />
                      </div>
                      <p className="text-xs text-dark-500 ml-10">
                        {isHigh ? high : isLow ? low : 'Balanced'}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Beliefs */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-dark-100 flex items-center gap-2">
                <Heart className="w-5 h-5 text-pink-400" />
                Current Beliefs
              </h3>
              <button
                onClick={() => toggleSection('beliefs')}
                className="text-dark-400 hover:text-dark-100 text-sm"
              >
                {expandedSections.beliefs ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
            </div>
            
            {expandedSections.beliefs && (
              <div style={{ animation: 'animateIn 0.2s ease-out' }}>
                {Object.entries(persona.beliefs).length === 0 ? (
                  <p className="text-dark-500 text-center py-4">No strong beliefs formed yet</p>
                ) : (
                  <div className="space-y-2">
                    {Object.entries(persona.beliefs).map(([topic, strength]) => (
                      <div key={topic} className="flex items-center justify-between p-3 bg-dark-800/50 rounded-lg">
                        <span className="text-dark-300 capitalize">{topic.replace(/_/g, ' ')}</span>
                        <div className="flex items-center gap-3">
                          <div className="w-24 h-2 bg-dark-700 rounded-full overflow-hidden">
                            <div 
                              className={clsx('h-full rounded-full transition-all duration-500', 
                                strength > 0 ? 'bg-green-500' : strength < 0 ? 'bg-red-500' : 'bg-gray-500'
                              )}
                              style={{ width: `${Math.abs(strength) * 100}%` }}
                            />
                          </div>
                          <span className={clsx('text-sm font-medium', 
                            strength > 0.3 ? 'text-green-400' : 
                            strength < -0.3 ? 'text-red-400' : 'text-yellow-400'
                          )}>
                            {strength > 0 ? 'FOR' : strength < 0 ? 'AGAINST' : 'NEUTRAL'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Trust Levels */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-dark-100 flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-400" />
                Trust Levels
              </h3>
              <button
                onClick={() => toggleSection('trust')}
                className="text-dark-400 hover:text-dark-100 text-sm"
              >
                {expandedSections.trust ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
            </div>
            
            {expandedSections.trust && (
              <div style={{ animation: 'animateIn 0.2s ease-out' }}>
                {Object.entries(persona.trust_levels).length === 0 ? (
                  <p className="text-dark-500 text-center py-4">No trust relationships established</p>
                ) : (
                  <div className="space-y-2">
                    {Object.entries(persona.trust_levels).map(([targetId, trust]) => {
                      const target = usePersonaStore.getState().getPersonaSummary(targetId);
                      return (
                        <div key={targetId} className="flex items-center justify-between p-3 bg-dark-800/50 rounded-lg">
                          <div className="flex items-center gap-3">
                            <div className={clsx(
                              'w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white',
                              target?.gender === 'female' ? 'bg-pink-500' : 'bg-blue-500'
                            )}>
                              {target?.name.charAt(0)}
                            </div>
                            <span className="text-dark-300">{target?.name || targetId.slice(0, 8)}</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <div className="w-24 h-2 bg-dark-700 rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-blue-500 rounded-full transition-all duration-500"
                                style={{ width: `${trust * 100}%` }}
                              />
                            </div>
                            <span className={clsx('text-sm font-medium',
                              trust > 0.7 ? 'text-green-400' :
                              trust > 0.4 ? 'text-yellow-400' : 'text-red-400'
                            )}>
                              {Math.round(trust * 100)}%
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Private Thoughts */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-dark-100 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-400" />
                Private Thoughts (Hidden)
              </h3>
              <button
                onClick={() => toggleSection('private')}
                className="text-dark-400 hover:text-dark-100 text-sm"
              >
                {expandedSections.private ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
            </div>
            
            {expandedSections.private && (
              <div style={{ animation: 'animateIn 0.2s ease-out' }}>
                <p className="text-xs text-dark-500 mb-3">
                  These are internal monologues not shared with other personas. 
                  They reveal true beliefs, doubts, and strategic thinking.
                </p>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {persona.private_thoughts.length === 0 ? (
                    <p className="text-dark-500 text-center py-4">No private thoughts recorded</p>
                  ) : (
                    persona.private_thoughts.slice(-5).map((thought, i) => (
                      <div key={i} className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-lg text-sm text-purple-300">
                        {thought}
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}