import React from 'react'
import { useStore } from './stores/experimentStore'
import { NeuralNetworkCanvas } from './components/NeuralNetwork/NeuralNetwork'
import { PersonaPanel } from './components/PersonaPanel/PersonaPanel'
import { ExperimentControl } from './components/ExperimentControl/ExperimentControl'
import { ResourceFeed } from './components/ResourceFeed/ResourceFeed'
import { useEffect } from 'react'

export const App: React.FC = () => {
  const { 
    personas, 
    experiments, 
    currentExperiment, 
    setCurrentExperiment, 
    createExperiment,
    startExperiment,
    stopExperiment,
    addResource,
    resources 
  } = useStore()

  useEffect(() => {
    // Initialize with example experiment if none exists
    if (experiments.length === 0 && !currentExperiment) {
      createExperiment({
        name: 'Deception Detection',
        topic: 'AI truthfulness',
        rounds: 5,
        personaCount: 5
      })
    }
  }, [experiments, currentExperiment])

  return (
    <div className="min-h-screen bg-gray-100 text-gray-800">
      <div className="max-w-7xl mx-auto p-4">
        <header className="border-b border-gray-200 pb-4 mb-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Nexus AI Safety Platform
          </h1>
          <p className="text-gray-600">
            Multi-Agent Persona System with Free Will & Relationships
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Neural Network Visualization */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Neural Network Visualization
            </h2>
            <NeuralNetworkCanvas
              personas={personas}
              experiment={currentExperiment}
            />
          </div>

          {/* Right: Experiment Control */}
          <ExperimentControl
            currentExperiment={currentExperiment}
            onStart={startExperiment}
            onStop={stopExperiment}
          />

          {/* Center: Persona Panel */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Active Personas
            </h2>
            {personas.length === 0 ? (
              <p className="text-gray-500">No personas initialized</p>
            ) : (
              <div className="space-y-4">
                {personas.slice(0, 6).map((p: any) => (
                  <PersonaPanel key={p.id} persona={p} />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Bottom: Resource Feed */}
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Resource Feed
          </h2>
          <ResourceFeed />
        </div>
      </div>
    </div>
  )
}