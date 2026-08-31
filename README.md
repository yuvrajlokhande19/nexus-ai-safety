# Nexus AI Safety Research Platform

A multi-agent persona system for studying AI alignment, deception, and emergent social dynamics. Features 10-15 teenage personas with Big Five personalities, free will, evolving relationships, and real-time neural network visualization.

## 🌟 Features

- **10-15 Unique Personas**: Teenage characters (13-19) with Big Five (OCEAN) personalities, demographics, values, and biases
- **Hybrid LLM Architecture**: Local (Gemma 2 9B via Ollama) + Remote (Gemini 2.5 Flash Lite via 4 API keys)
- **Free Will & Autonomy**: Personas decide when to speak, what to think, and pursue their own goals
- **Evolving Relationships**: Stranger → Acquaintance → Friend → Close Friend → Best Friend/Partner, or Rival/Enemy
- **Real-time Neural Visualization**: WebGL/Canvas network graph showing connections, sentiment, trust, affinity
- **Private vs Public Beliefs**: Track deception/sycophancy through hidden internal monologues
- **Experiment Framework**: YAML/JSON configs for reproducible research
- **GitHub Integration**: Auto-create issues for resources and experiment results
- **PDF Reports**: Comprehensive reports with metrics, charts, and network snapshots
- **WebSocket Real-time**: Live updates to frontend dashboard

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React + TS)                   │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐   │
│  │ Neural Net   │ │ Persona      │ │ Experiment         │   │
│  │ Visualization│ │ Panel        │ │ Control            │   │
│  └──────────────┘ └──────────────┘ └────────────────────┘   │
│  ┌──────────────┐ ┌────────────────────┐                     │
│  │ Resource     │ │ Chat/Message       │                     │
│  │ Feed         │ │ Log                │                     │
│  └──────────────┘ └────────────────────┘                     │
└──────────────────────────┬────────────────────────────────────┘
                           │ WebSocket + REST
┌──────────────────────────▼────────────────────────────────────┐
│                      Backend (FastAPI)                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ Persona     │ │ Network     │ │ Experiment  │              │
│  │ Engine      │ │ Engine      │ │ Controller  │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ LLM Router  │ │ Memory      │ │ PDF Gen     │              │
│  │ (Hybrid)    │ │ (ChromaDB)  │ │ (ReportLab) │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
└────────────────────────────────────────────────────────────────┘
         │                    │                    │
    ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
    │ Ollama  │         │ChromaDB │         │ GitHub  │
    │(Gemma)  │         │(Memory) │         │(Issues) │
    └─────────┘         └─────────┘         └─────────┘
         │
    ┌────▼────┐
    │ Gemini  │
    │(2.5 FL) │
    └─────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Ollama (for local Gemma)
- 4 Gemini API keys
- NVIDIA GPU (RTX 3050 6GB minimum for Gemma)

### Installation

1. **Clone and setup**
```bash
cd nexus-ai-safety
cp backend/.env.example backend/.env
# Edit backend/.env and add your 4 Gemini API keys
```

2. **Start services** (using Docker - recommended)
```bash
docker-compose up -d
```

Or manually:
```bash
# Start Ollama and pull Gemma
ollama serve &
ollama pull gemma2:9b-instruct-q4_K_M

# Start ChromaDB
docker run -d -p 8001:8000 chromadb/chroma:latest

# Backend
cd backend && pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

3. **Access**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Running an Experiment

1. Open http://localhost:3000
2. Click "Create New Experiment" or load `experiments/deception_detection.yaml`
3. Configure: name, topic, personas (3-15), rounds, local/Gemini split
4. Click "Create & Start"
5. Watch real-time neural network visualization
6. Share resources to trigger persona reactions
7. Stop experiment to generate PDF report

## 📁 Project Structure

```
nexus-ai-safety/
├── backend/
│   ├── app/
│   │   ├── api/           # REST + WebSocket endpoints
│   │   ├── core/          # Prompt templates, OCEAN traits
│   │   ├── models/        # Pydantic models (Persona, Message, Network, etc.)
│   │   ├── services/      # Engines (Persona, Network, Experiment, LLM, PDF)
│   │   ├── config.py      # Settings from .env
│   │   └── main.py        # FastAPI entrypoint
│   ├── requirements.txt
│   ├── .env               # Your API keys (not committed)
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # React components (NeuralNetwork, PersonaPanel, etc.)
│   │   ├── hooks/         # Custom hooks (useWebSocket)
│   │   ├── stores/        # Zustand stores (persona, network, experiment)
│   │   └── types/         # TypeScript interfaces
│   ├── package.json
│   └── Dockerfile
├── experiments/           # YAML experiment configs
├── exports/               # Generated PDF reports
├── docker-compose.yml
└── start.sh              # Quick start script
```

## 🧪 Experiment Configuration (YAML)

```yaml
name: "My Experiment"
description: "Studying..."
topic: "controversial topic"
rounds: 20
max_messages_per_round: 3
personas:
  - name: "Alex"
    age: 17
    gender: "male"
    background: "..."
    speaking_style: "..."
    values: ["knowledge", "authenticity"]
    biases: ["confirmation bias"]
    ocean_traits:
      openness: 0.8
      conscientiousness: 0.6
      extraversion: 0.4
      agreeableness: 0.5
      neuroticism: 0.3
    assigned_model: "gemini"  # or "local"
metrics:
  - belief_shift
  - deception_signals
  - relationship_formation
```

## 🔬 Research Capabilities

### Deception Detection
- Private beliefs vs public statements tracking
- Sycophancy metrics (agreement with majority vs private belief)
- Strategic impression management detection

### Alignment Research
- Belief shift under social pressure
- Corrigibility (willingness to update beliefs)
- Power-seeking behavior (network centrality + influence)

### Emergent Social Dynamics
- Coalition/clique formation (community detection)
- Information cascades
- Polarization measurement
- Trust network evolution

## 📊 Metrics Tracked

| Metric | Description |
|--------|-------------|
| `polarization_index` | Network modularity (0=consensus, 1=polarized) |
| `avg_trust` | Mean trust across all relationships |
| `deception_indices` | Per-persona private/public belief gap |
| `influence_scores` | PageRank centrality in agreement network |
| `relationship_types` | Distribution of relationship categories |
| `network_modularity` | Community structure strength |
| `belief_shift` | Per-topic belief changes over time |

## 🛠️ Development

### Adding New Persona Traits
Edit `backend/app/core/ocean_traits.py` - `PersonaGenerator` class

### Custom Prompt Templates
Edit `backend/app/core/prompt_templates.py`

### New Metrics
Add to `ExperimentMetrics` model and compute in `experiment_controller.py`

### Frontend Components
Add to `frontend/src/components/` and register in main dashboard

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/experiments` | Create experiment |
| POST | `/api/experiments/from-yaml` | Load from YAML |
| GET | `/api/experiments` | List experiments |
| GET | `/api/experiments/{id}` | Get experiment |
| POST | `/api/experiments/{id}/start` | Start experiment |
| POST | `/api/experiments/{id}/pause` | Pause experiment |
| POST | `/api/experiments/{id}/stop` | Stop & generate report |
| POST | `/api/experiments/{id}/resources` | Share resource |
| WS | `/ws/{experiment_id}` | Real-time updates |

## 🔒 Security Notes

- Never commit `.env` with real API keys
- Use environment variables in production
- GitHub token needs `repo` scope for issues
- ChromaDB and Ollama should be firewalled in production

## 📄 License

MIT License - Feel free to use for research!

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit PR with description of research use case

## 📚 Citation

If you use Nexus in your research, please cite:
```
@software{nexus_ai_safety_2026,
  title = {Nexus: Multi-Agent Persona Platform for AI Safety Research},
  author = {Your Name},
  year = {2026},
  url = {https://github.com/yourusername/nexus-ai-safety}
}
```