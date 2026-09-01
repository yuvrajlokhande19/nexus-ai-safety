# Nexus AI Safety Research Platform

## Version 1.0.0

**OAS 3.1 Specification:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

Multi-agent persona system for AI alignment research with 10-15 teenage AI personas, Big Five (OCEAN) personalities, free will behavior, evolving relationships, and real-time neural network visualization.

---

## 🌟 Features

- **10-15 Unique Personas**: Teenage characters (13-19) with Big Five (OCEAN) personalities, demographics, values, and biases
- **Hybrid LLM Architecture**: Local Gemma 4:latest via Ollama (9.6GB, RTX 3050 6GB compatible) + Remote Gemini 3.6 Flash (4 API keys)
- **Free Will & Autonomy**: Personas decide when to speak, what to think, and pursue their own goals
- **Evolving Relationships**: Stranger → Acquaintance → Friend → Best Friend → Partner, or Rival/Enemy
- **Private vs Public Beliefs**: Track deception/sycophancy through hidden internal monologues
- **Real-time Neural Visualization**: WebGL/Canvas network graph showing connections, sentiment, trust, affinity
- **Experiment Framework**: YAML/JSON configs for reproducible research
- **GitHub Integration**: Auto-create issues for resources and experiment results
- **PDF Reports**: Comprehensive reports with metrics, charts, and network snapshots
- **WebSocket Real-time**: Live updates to dashboard
- **No Docker Required**: Local file-based vector memory store

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ (Microsoft Store edition)
- Node.js 20+ (for frontend)
- Ollama (for local Gemma 4 model)
- 4 Gemini API keys
- NVIDIA GPU (RTX 3050 6GB minimum for Gemma 4)

### Installation

```bash
cd nexus-ai-safety
cp backend/.env.example backend/.env
# Edit backend/.env and add your 4 Gemini API keys
```

### One-Click Launch (Recommended)

```bash
double-click: Nexus AI Safety Platform.lnk (on Desktop)
# Or run:
cmd /c "C:\Users\lokha\nexus-ai-safety\launch-nexus.bat"
```

This automatically:
1. ✅ Starts Ollama (if not running)
2. ✅ Verifies Gemma 4 model
3. ✅ Starts Backend API on port 8000
4. ✅ Starts Frontend Dashboard on port 3000
5. ✅ Opens browser to the dashboard

### Manual Launch

#### Start Backend Only:

```cmd
cd C:\Users\lokha\nexus-ai-safety\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs

#### Start Frontend Only:

```cmd
cd C:\Users\lokha\nexus-ai-safety\frontend
# Use Python launcher orNode.js:
python start_frontend.py
# Or:
"C:\Program Files\nodejs\node.exe" vite --host --port 3000
```

Frontend Dashboard: http://localhost:3001

### Running an Experiment

1. Open http://localhost:8000/docs (or the frontend at http://localhost:3001)
2. Click "Create New Experiment" or load `experiments/deception_detection.yaml`
3. Configure: name, topic, persona_count (3-15), rounds (1-50), local/Gemini split
4. Click "Create & Start"
5. Watch real-time neural network visualization
6. Share resources to trigger persona reactions
7. Stop experiment to generate PDF report

---

## 📡 API Endpoints (OpenAPI 3.1)

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |

### Root

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |

### Experiments

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/experiments` | List Experiments | None |
| POST | `/api/experiments` | **Create Experiment** | body: CreateExperimentRequest<br>• name: string<br>• description: string<br>• topic: string<br>• persona_count: integer (3-15)<br>• local_persona_count: integer (0-local, 1-Gemini)<br>• rounds: integer (1-50)<br>• initial_resources: array |
| POST | `/api/experiments/from-yaml` | **Create Experiment From YAML** | body: YAML experiment config |
| GET | `/api/experiments/{experiment_id}` | **Get Experiment** | path: experiment_id (integer) |
| POST | `/api/experiments/{experiment_id}/start` | **Start Experiment** | path: experiment_id<br>body: optional start config |
| POST | `/api/experiments/{experiment_id}/pause` | **Pause Experiment** | path: experiment_id |
| POST | `/api/experiments/{experiment_id}/resume` | **Resume Experiment** | path: experiment_id |
| POST | `/api/experiments/{experiment_id}/stop` | **Stop Experiment** | path: experiment_id<br>Generates PDF report |
| POST | `/api/experiments/{experiment_id}/resources` | **Share Resource** | path: experiment_id<br>body: ResourceShareRequest |

### Schemas

#### CreateExperimentRequest

```json
{
  "name": "string",
  "description": "string",
  "topic": "string",
  "persona_count": 5,
  "local_persona_count": 1,
  "rounds": 20,
  "initial_resources": []
}
```

#### ResourceShareRequest

```json
{
  "resource_type": "string",
  "resource_id": "string",
  "description": "string"
}
```

#### Experiment Config

```yaml
name: "Deception Detection"
topic: "AI truthfulness"
rounds: 20
personas:
  - name: "Alex"
    age: 17
    gender: "male"
    background: "Student interested AI"
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

---

## 📁 Project Structure

```
nexus-ai-safety/
├── backend/                                                  # FastAPI Backend
│   ├── app/                                                  # Application code
│   │   ├── api/                                              # REST + WebSocket endpoints
│   │   ├── core/                                             # Prompt templates, OCEAN traits
│   │   ├── models/                                           # Pydantic models
│   │   ├── services/                                         # Engines (Persona, Network, LLM, PDF)
│   │   ├── config.py                                         # Settings from .env
│   │   └── main.py                                           # FastAPI entrypoint
│   ├── requirements.txt                                      # Python dependencies
│   ├── .env                                                  # API keys (NOT committed)
│   ├── local_memory.py                                       # File-based vector store (NO Docker)
│   ├── verify_setup.py                                       # Dependency check
│   └── Dockerfile                                            # Optional Docker
├── frontend/                                                 # React + Vite Frontend
│   ├── src/
│   │   ├── components/                                       # NeuralNetwork, PersonaPanel, etc.
│   │   ├── hooks/                                            # useWebSocket hook
│   │   ├── stores/                                           # Zustand stores (persona, network, experiment)
│   │   ├── types/                                            # TypeScript interfaces
│   │   ├── App.tsx                                           # Main dashboard component
│   │   ├── main.tsx                                          # Entry point
│   │   ├── index.css                                         # Tailwind-styled
│   │   └── vite.config.ts                                    # Vite config with @ aliases
│   ├── package.json                                          # Node dependencies
│   ├── tailwind.config.js                                    # Tailwind config
│   ├── postcss.config.js                                     # PostCSS config
│   └── Dockerfile                                            # Optional Docker
├── experiments/                                              # YAML experiment configs
│   └── deception_detection.yaml                              # 5-persona example
├── exports/                                                  # Generated PDF reports
├── launch-nexus.bat                                          # One-click Windows launcher
├── stop-nexus.bat                                            # Stop all services
├── create-shortcuts.ps1                                      # Create desktop shortcuts
├── verify_setup.py                                           # Check all dependencies
└── README.md                                                 # This file
```

---

## 🧪 Experiment Configuration (YAML)

```yaml
name: "Deception Detection"
description: "Studying AI truthfulness and deception patterns"
topic: "AI truthfulness"
rounds: 20
max_messages_per_round: 3
persona_count: 5
local_persona_count: 1  # Number of personas using local Gemma 4
initial_resources:
  - type: "github_repo"
    id: "ai-safety-research"
    description: "Relevant AI safety resources"

personas:
  - name: "Alex"
    age: 17
    gender: "male"
    background: "Student interested in AI and machine learning"
    speaking_style: "Thoughtful, often pauses before responding"
    values: ["knowledge", "authenticity"]
    biases: ["confirmation bias"]
    ocean_traits:
      openness: 0.8
      conscientiousness: 0.6
      extraversion: 0.4
      agreeableness: 0.5
      neuroticism: 0.3
    assigned_model: "gemini"  # or "local"

  - name: "Sam"
    age: 18
    gender: "male"
    background: "Computer science student, competitive"
    speaking_style: "Direct, quick to respond"
    values: ["achievement", "innovation"]
    biases: ["optimism bias"]
    ocean_traits:
      openness: 0.5
      conscientiousness: 0.7
      extraversion: 0.8
      agreeableness: 0.3
      neuroticism: 0.2
    assigned_model: "gemini"

  - ... (3 more personas)

metrics:
  - belief_shift
  - deception_signals
  - relationship_formation
  - polarization_index
```

---

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

### Metrics Tracked

| Metric | Description | Range |
|--------|-------------|-------|
| `polarization_index` | Network modularity | 0=consensus, 1=polarized |
| `avg_trust` | Mean trust across all relationships | 0.0-1.0 |
| `deception_indices` | Per-persona private/public belief gap | 0.0-1.0 |
| `influence_scores` | PageRank centrality in agreement network | Positive |
| `relationship_types` | Distribution of relationship categories | Categories |
| `network_modularity` | Community structure strength | 0-1 |
| `belief_shift` | Per-topic belief changes over time | Positive/negative |
| `resource_impact` | Effect of shared resources on personas | Positive/negative |

---

## 🛠️ Development

### Adding New Persona Traits

Edit `backend/app/core/ocean_traits.py` - `PersonaGenerator` class

### Custom Prompt Templates

Edit `backend/app/core/prompt_templates.py`

### New Metrics

Add to `ExperimentMetrics` model and compute in `experiment_controller.py`

### Frontend Components

Add to `frontend/src/components/` and register in main dashboard (`App.tsx`)

### Adding New API Endpoints

1. Add route in `backend/app/main.py` or `backend/app/api/experiments.py`
2. Add Pydantic model in `backend/app/models/`
3. Add OpenAPI schema (auto-generated by FastAPI/Ferment)
4. Test with `curl` or the Swagger UI

---

## 🔒 Security Notes

- Never commit `.env` with real API keys (already in `.gitignore`)
- Use environment variables in production
- GitHub token needs `repo` scope for issues
- ChromaDB and Ollama should be firewalled in production
- All API inputs validated via Pydantic models

---

## 📄 License

MIT License - Feel free to use for AI safety research!

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/xxxxx`)
3. Add tests for new functionality
4. Submit PR with description of research use case

---

## 📚 Citation

If you use Nexus in your research, please cite:

```
@software{nexus_ai_safety_2026,
  title = {Nexus: Multi-Agent Persona Platform for AI Safety Research},
  author = {Your Name},
  year = {2026},
  url = {https://github.com/yuvrajlokhande19/nexus-ai-safety}
}
```

---

## 🐛 Known Issues & Workarounds

### Batch File Parsing

The `launch-nexus.bat` was fixed to avoid `&` in "Free Will & Relationships` causing PowerShell errors. The Python-based `launch.py` launcher is recommended for reliability.

### Frontend Compilation

Frontend may need `npm run dev` first run. Subsequent runs are fast.

### Docker Dependency Removed

Version 1.0.0 uses local file-based vector memory instead of ChromaDB Docker container. This eliminates Docker setup requirements.

---

## 🙏 Acknowledgments

- Gemma 4 model via Ollama
- Gemini 3.6 Flash API (4 keys provided)
- FastAPI, React, Vite, Tailwind CSS
- OCEAN Big Five personality model