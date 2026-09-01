#!/usr/bin/env python
"""
Nexus AI Safety Platform - Reliable Launcher
Starts both Backend (FastAPI) and Frontend (React Vite) services.
Uses Python subprocess to avoid batch/powershell parsing errors.
"""
import subprocess
import sys
import time
import os
import urllib.request

PROJECT_DIR = r"C:\Users\lokha\nexus-ai-safety"
BACKEND_DIR = os.path.join(PROJECT_DIR, "backend")
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")

def start_backend():
    """Start the FastAPI backend server."""
    print("Starting Backend API (FastAPI + Uvicorn)...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Wait and verify it's running
    for _ in range(15):
        time.sleep(1)
        try:
            r = urllib.request.urlopen('http://localhost:8000/docs', timeout=3)
            print("  Backend API running on http://localhost:8000")
            return proc
        except:
            continue
    print("  Backend starting... check console output")
    return proc

def start_frontend():
    """Start the React Vite frontend dashboard."""
    print("Starting Frontend Dashboard (React + Vite)...")
    node_exe = r"C:\Program Files\nodejs\node.exe"
    if not os.path.exists(node_exe):
        print("  Node.js not found at expected path")
        print("  Frontend will be skipped - use browser at http://localhost:8000/docs")
        return None
    
    proc = subprocess.Popen(
        [node_exe, "vite", "--host", "--port", "3001"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for Vite to be ready
    for i in range(25):
        time.sleep(1)
        try:
            r = urllib.request.urlopen('http://localhost:3001', timeout=2)
            print("  Frontend Dashboard running on http://localhost:3001")
            return proc
        except:
            if i >= 15:
                print("  Vite compiling... please wait...")
            continue
    
    print("  Frontend still starting... check the console window")
    return proc

def main():
    print("NEXUS AI SAFETY RESEARCH PLATFORM")
    print("Initializing services...")
    
    # Start backend
    backend_proc = start_backend()
    print()
    
    # Start frontend
    frontend_proc = start_frontend()
    print()
    
    print("NEXUS PLATFORM OPERATIONAL")
    print("Service URLs:")
    print("  Dashboard:      http://localhost:3001")
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
    print("Press CTRL+C to stop. Services continue in background.")
    
    # Keep alive
    try:
        while True:
            time.sleep(5)
            try:
                r = urllib.request.urlopen('http://localhost:8000/api/health', timeout=2)
            except:
                pass
            try:
                r = urllib.request.urlopen('http://localhost:3001', timeout=2)
            except:
                pass
    except KeyboardInterrupt:
        print("\nStopping Nexus Platform...")
        if 'backend_proc' in dir() and backend_proc:
            backend_proc.terminate()
        if 'frontend_proc' in dir() and frontend_proc:
            frontend_proc.terminate()
        print("Done.")

if __name__ == "__main__":
    main()