#!/usr/bin/env python
"""
Nexus AI Safety Platform - One-Click Launcher
Launches both Backend (FastAPI) and Frontend (React Vite) services.
Avoids batch/powershell parsing issues with spaces in paths.
"""
import subprocess
import sys
import time
import os

print("=" * 60)
print("NEXUS AI SAFETY RESEARCH PLATFORM")
print("=" * 60)
print()

# Configuration
PROJECT_DIR = r"C:\Users\lokha\nexus-ai-safety"
BACKEND_DIR = os.path.join(PROJECT_DIR, "backend")
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")

# Start Backend (FastAPI)
print("[1/4] Starting Backend API (FastAPI + Uvicorn)...")
backend_proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app",
     "--host", "0.0.0.0", "--port", "8000", "--reload"],
    cwd=BACKEND_DIR,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
print("   Backend process started (PID:%d)" % backend_proc.pid)
time.sleep(3)

# Check if backend is up
try:
    import urllib.request
    r = urllib.request.urlopen('http://localhost:8000/docs', timeout=5)
    print("   Backend API running on http://localhost:8000")
except Exception as e:
    print("   Backend still starting (may take a moment)")

print()
print("[2/4] Starting Frontend Dashboard (React + Vite)...")
print()

# Start Frontend (React Vite)
try:
    frontend_proc = subprocess.Popen(
        [r"C:\Program Files\nodejs\node.exe", "vite", "--host", "--port", "3000"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    print("   Frontend process started (PID:%d)" % frontend_proc.pid)
    print("   Waiting for Vite compilation...")
    
    # Wait for frontend to be ready
    for i in range(20):  # Try for 20 seconds
        time.sleep(1)
        try:
            import urllib.request
            r = urllib.request.urlopen('http://localhost:3000', timeout=2)
            print("   Frontend Dashboard running on http://localhost:3000")
            break
        except Exception:
            if i >= 15:
                print("   Frontend still compiling... check console")
            continue
            
except FileNotFoundError:
    print("   Node.js not found - skipping frontend start")

print()
print("=" * 60)
print("NEXUS AI SAFETY PLATFORM IS NOW RUNNING")
print("=" * 60)
print()
print("Access Points:")
print("  Dashboard:      http://localhost:3000")
print("  Backend API:    http://localhost:8000")
print("  API Docs:       http://localhost:8000/docs")
print()
print("Features:")
print("  10-15 Teenage Personas with OCEAN Personalities")
print("  Free Will & Autonomous Decision Making")
print("  Evolving Relationships (Friends/Rivals/Partners)")
print("  Private vs Public Belief Tracking")
print("  Real-time Neural Network Visualization")
print("  Hybrid LLM: Local Gemma 4 + Gemini 3.6 Flash (4 keys)")
print("  YAML Experiment Configs + PDF Reports")
print()
print("Press CTRL+C to stop (services will continue in background)")

# Keep alive
try:
    while True:
        time.sleep(5)
        try:
            import urllib.request
            r = urllib.request.urlopen('http://localhost:8000/api/health', timeout=2)
        except:
            pass
        try:
            r = urllib.request.urlopen('http://localhost:3000', timeout=2)
        except:
            pass
except KeyboardInterrupt:
    print("\nStopping Nexus Platform...")
    if 'backend_proc' in dir() and backend_proc:
        backend_proc.terminate()
    if 'frontend_proc' in dir() and frontend_proc:
        frontend_proc.terminate()
    print("Done.")