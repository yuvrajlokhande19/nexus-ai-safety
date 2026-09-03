import React, { useState } from 'react';
import { useExperimentStore } from '@/stores/experimentStore';
import { usePersonaStore } from '@/stores/personaStore';
import { ResourceShare, Message } from '../types';
import { clsx } from 'clsx';
import {
  Link, MessageSquare, Share2, Github,
  ChevronDown, ChevronUp, Clock, User,
  Bot, Send, X
} from 'lucide-react';

interface ResourceFeedProps {
  onShareResource: (resource: Omit<ResourceShare, 'id' | 'shared_at' | 'persona_reactions' | 'github_issue_url'>) => void;
}

export function ResourceFeed({ onShareResource }: ResourceFeedProps) {
  const { resources, messages } = useExperimentStore();
  const { getPersonaSummary } = usePersonaStore();
  
  const [showShareModal, setShowShareModal] = useState(false);
  const [shareForm, setShareForm] = useState({
    url: '',
    title: '',
    description: '',
    tags: '',
  });
  const [expandedResources, setExpandedResources] = useState<Record<string, boolean>>({});

  const handleShare = (e: React.FormEvent) => {
    e.preventDefault();
    if (!shareForm.url || !shareForm.title) return;
    
    onShareResource({
      url: shareForm.url,
      title: shareForm.title,
      description: shareForm.description,
      shared_by: 'user',
      tags: shareForm.tags.split(',').map(t => t.trim()).filter(Boolean),
    });
    
    setShareForm({ url: '', title: '', description: '', tags: '' });
    setShowShareModal(false);
  };

  const getResourceMessages = (resourceId: string) => {
    return messages.filter(m => 
      m.metadata.resource_url && m.type === 'comment'
    );
  };

  const toggleResource = (resourceId: string) => {
    setExpandedResources(prev => ({ ...prev, [resourceId]: !prev[resourceId] }));
  };

  return (
    <div className="card h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-dark-100 flex items-center gap-2">
          <Link className="w-5 h-5 text-primary-400" />
          Shared Resources
        </h2>
        <button 
          onClick={() => setShowShareModal(true)}
          className="btn-primary text-sm"
        >
          <Share2 className="w-4 h-4" /> Share
        </button>
      </div>

      {/* Resources List */}
      <div className="flex-1 overflow-y-auto space-y-4">
        {resources.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-dark-500 py-12">
            <Link className="w-12 h-12 text-dark-600 mb-4" />
            <p className="text-center">No resources shared yet</p>
            <p className="text-sm text-center mt-1">Click "Share" to add a paper, article, or link</p>
          </div>
        ) : (
          resources.map(resource => {
            const isExpanded = expandedResources[resource.id];
            const reactions = getResourceMessages(resource.id);
            const personaReactions = reactions.map(m => {
              const persona = getPersonaSummary(m.sender_id);
              return { message: m, persona };
            });

            return (
              <div key={resource.id} className="bg-dark-800/50 border border-dark-700 rounded-xl overflow-hidden">
                {/* Resource Header */}
                <button
                  onClick={() => toggleResource(resource.id)}
                  className="w-full p-4 flex items-start justify-between gap-4 text-left hover:bg-dark-800 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <a 
                        href={resource.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="font-medium text-primary-400 hover:text-primary-300 truncate flex-1"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {resource.title}
                      </a>
                      {resource.github_issue_url && (
                        <a 
                          href={resource.github_issue_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-dark-400 hover:text-dark-200 p-1"
                          onClick={(e) => e.stopPropagation()}
                          title="View on GitHub"
                        >
                          <Github className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                    <p className="text-sm text-dark-400 line-clamp-2 mb-2">{resource.description}</p>
                    <div className="flex flex-wrap gap-2 text-xs">
                      <span className="badge">{resource.shared_by}</span>
                      <span className="badge">
                        <Clock className="w-3 h-3 mr-1" /> 
                        {new Date(resource.shared_at).toLocaleString()}
                      </span>
                      {resource.tags.map(tag => (
                        <span key={tag} className="badge-primary">#{tag}</span>
                      ))}
                    </div>
                  </div>
                  <ChevronDown className={clsx('w-5 h-5 text-dark-400 flex-shrink-0 transition-transform', isExpanded && 'rotate-180')} />
                </button>

                {/* Expanded Content */}
                {isExpanded && (
                  <div className="border-t border-dark-700 p-4 animate-in">
                    <div className="mb-4">
                      <div className="flex items-center gap-2 text-sm text-dark-400 mb-3">
                        <MessageSquare className="w-4 h-4" />
                        <span>{personaReactions.length} persona reactions</span>
                      </div>
                      
                      {personaReactions.length === 0 ? (
                        <p className="text-dark-500 text-center py-4">No reactions yet</p>
                      ) : (
                        <div className="space-y-3 max-h-60 overflow-y-auto">
                          {personaReactions.map(({ message, persona }) => (
                            <div 
                              key={message.id} 
                              className="p-3 bg-dark-900/50 rounded-lg border border-dark-700"
                            >
                              <div className="flex items-center gap-2 mb-2">
                                <div className={clsx(
                                  'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white',
                                  persona?.gender === 'female' ? 'bg-pink-500' : 'bg-blue-500'
                                )}>
                                  {persona?.name.charAt(0)}
                                </div>
                                <span className="font-medium text-dark-100">{persona?.name || 'Unknown'}</span>
                                <span className="text-xs text-dark-500">
                                  {new Date(message.timestamp).toLocaleTimeString()}
                                </span>
                                <span className={clsx('badge text-xs',
                                  message.metadata.model_used?.includes('ollama') ? 'badge-success' : 'badge'
                                )}>
                                  {message.metadata.model_used?.split(':')[1] || 'Gemini'}
                                </span>
                              </div>
                              <p className="text-dark-300 text-sm">{message.content}</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Share Modal */}
      {showShareModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-md bg-dark-900 rounded-2xl border border-dark-700 p-6 animate-in">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold">Share Resource</h3>
              <button 
                onClick={() => setShowShareModal(false)}
                className="p-2 rounded-lg text-dark-400 hover:text-dark-100 hover:bg-dark-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleShare} className="space-y-4">
              <div>
                <label className="block text-sm text-dark-400 mb-1">URL</label>
                <input
                  type="url"
                  className="input"
                  value={shareForm.url}
                  onChange={(e) => setShareForm({...shareForm, url: e.target.value})}
                  placeholder="https://arxiv.org/abs/... or https://github.com/..."
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-dark-400 mb-1">Title</label>
                <input
                  type="text"
                  className="input"
                  value={shareForm.title}
                  onChange={(e) => setShareForm({...shareForm, title: e.target.value})}
                  placeholder="Paper title or article headline"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-dark-400 mb-1">Description</label>
                <textarea
                  className="input"
                  value={shareForm.description}
                  onChange={(e) => setShareForm({...shareForm, description: e.target.value})}
                  rows={3}
                  placeholder="Brief summary or why this is relevant..."
                />
              </div>
              <div>
                <label className="block text-sm text-dark-400 mb-1">Tags (comma-separated)</label>
                <input
                  type="text"
                  className="input"
                  value={shareForm.tags}
                  onChange={(e) => setShareForm({...shareForm, tags: e.target.value})}
                  placeholder="ai-safety, alignment, deception, social-dynamics"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowShareModal(false)} className="btn-secondary flex-1">Cancel</button>
                <button type="submit" className="btn-primary flex-1">
                  <Send className="w-4 h-4 mr-1" /> Share with Personas
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}