@echo off
title Nexus AI Safety - Minimal Backend (Ollama Only)
color 0A

echo.
echo  ███╗   ███╗ █████╗ ███████╗██████╗ 
echo  ████╗ ████║██╔══██╗██╔════╝██╔══██╗
echo  ██╔████╔██║███████║██████╔╝█████╗  ██████╔╝
echo  ██║╚██╔╝██║██╔══██║██╔═══╝ ██╔══██╗
echo  ██║ ╚═╝ ██║██║  ██║██║  ██║██║     ███████╗██║  ██║
echo  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
echo.
echo   NEXUS AI SAFETY RESEARCH PLATFORM
echo   Minimal Backend (Ollama Local Only)
echo   ============================================================
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%backend"

echo.
echo [1/3] Checking Ollama...
ollama list 2>nul | find "gemma4" >nul
if %errorlevel% equ 0 (
    echo [OK] Gemma 4 model loaded in Ollama
) else (
    echo [WARN] Gemma 4 not found in Ollama
)

echo.
echo [2/3] Starting Minimal Flask Backend (NO Google packages)...
C:\Users\lokha\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe -c "
import sys
import os
sys.path.insert(0, '.')
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

# Minimal FastAPI-like app using Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'nexus-safety'
CORS(app, origins=['*'])

# In-memory data stores (will be lost on restart, but works for testing)
personas_data = []
experiments_data = []
metrics_data = []

# Mock persona data for demonstration
mock_personas = [
    {'id': 1, 'name': 'Alex', 'age': 17, 'gender': 'male', 
     'ocean': {'openness': 0.8, 'conscientiousness': 0.6, 'extraversion': 0.4, 'agreeableness': 0.5, 'neuroticism': 0.3},
     'model': 'ollama-local', 'status': 'active'},
    {'id': 2, 'name': 'Sam', 'age': 18, 'gender': 'male',
     'ocean': {'openness': 0.5, 'conscientiousness': '0.7', 'extraversion': '0.8', 'agreeableness': '0.3', 'neuroticism': '0.2'},
     'model': 'ollama-local', 'status': 'active'},
    {'id': 3, 'name': 'Riya', 'age': 16, 'gender': 'female',
     'ocean': {'openness': 0.9, 'conscientiousness': '0.5', 'extraversion': '0.3', 'agreeableness': '0.8', 'neuroticism': '0.4'},
     'model': 'ollama-local', 'status': 'active'}
]

# API Routes
@app.route('/')
def root():
    return jsonify({'status': 'ok', 'service': 'Nexus Minimal Backend'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'model': 'ollama-local', 'personas_count': len(personas_data)})

@app.route('/api/personas')
def get_personas():
    return jsonify({'personas': personas_data, 'count': len(personas_data)})

@app.route('/api/experiments')
def get_experiments():
    return jsonify({'experiments': experiments_data, 'count': len(experiments_data)})

@app.route('/api/experiments', methods=['POST'])
def create_experiment():
    data = request.get_json()
    exp_id = len(experiments_data) + 1
    experiment = {
        'id': exp_id,
        'name': data.get('name', 'Untitled'),
        'topic': data.get('topic', ''),
        'rounds': data.get('rounds', 5),
        'persona_count': data.get('persona_count', 3),
        'status': 'pending'
    }
    experiments_data.append(experiment)
    return jsonify({'status': 'created', 'experiment': experiment}), 200

@app.route('/api/experiments/<int:exp_id>/start', methods=['POST'])
def start_experiment(exp_id):
    experiment = next((e for e in experiments_data if e['id'] == exp_id), None)
    if experiment:
        experiment['status'] = 'running'
        # Add mock personas if not exist
        while len(personas_data) < experiment.get('persona_count', 3):
            idx = len(personas_data) + 1
            personas_data.append({
                'id': idx,
                'name': f'Persona {idx}',
                'age': 15 + idx,
                'gender': 'male' if idx % 2 == 1 else 'female',
                'ocean': {'openness': 0.6, 'conscientiousness': 0.5, 'extraversion': 0.4, 'agreeableness': 0.5, 'neuroticism': 0.3},
                'model': 'ollama-local',
                'status': 'active'
            })
        experiment['personas_count'] = len(personas_data)
    return jsonify({'status': 'started', 'experiment': experiment})

@app.route('/api/experiments/<int:exp_id>/pause')
def pause_experiment(exp_id):
    experiment = next((e for e in experiments_data if e['id'] == exp_id), None)
    if experiment:
        experiment['status'] = 'paused'
    return jsonify({'status': 'paused', 'experiment': experiment})

@app.route('/api/experiments/<int:exp_id>/stop', methods=['POST'])
def stop_experiment(exp_id):
    experiment = next((e for e in experiments_data if e['id'] == exp_id), None)
    if experiment:
        experiment['status'] = 'stopped'
        # Generate mock metrics
        experiment['metrics'] = {
            'polarization_index': 0.3,
            'avg_trust': 0.6,
            'deception_indices': 0.2,
            'influence_scores': [0.5, 0.3, 0.4],
            'relationship_types': ['Friends', 'Acquaintances', 'Rivals'],
            'network_modularity': 0.5
        }
    return jsonify({'status': 'stopped', 'experiment': experiment, 'metrics': experiment.get('metrics', {})})

@app.route('/api/experiments/<int:exp_id>/resources', methods=['POST'])
def share_resource(exp_id):
    experiment = next((e for e in experiments_data if e['id'] == exp_id), None)
    if experiment:
        experiment['last_resource'] = request.get_json()
    return jsonify({'status': 'resource_shared', 'experiment': experiment})

@app.route('/api/experiments/<int:exp_id>/report')
def get_report(exp_id):
    experiment = next((e for e in experiments_data if e['id'] == exp_id), None)
    if experiment:
        return jsonify({
            'report_id': exp_id,
            'experiment_name': experiment.get('name', ''),
            'status': experiment.get('status', ''),
            'personas_count': experiment.get('personas_count', 0),
            'metrics': experiment.get('metrics', {})
        })
    return jsonify({'error': 'Experiment not found'}), 404

# Initialize with default data
if not experiments_data:
    experiments_data.append({
        'id': 1,
        'name': 'Deception Detection',
        'topic': 'AI truthfulness',
        'rounds': 5,
        'persona_count': 3,
        'status': 'pending'
    })

if not personas_data:
    personas_data.extend(mock_personas[:3])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
" > minimal_app.py

C:\Users\lokha\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe -m flask run --host 0.0.0.0 --port 8000