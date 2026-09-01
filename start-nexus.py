#!/usr/bin/env python
"""
Nexus AI Safety Platform - One-Click Launcher (WORKING VERSION)
Starts Backend (FastAPI) + Frontend (React Vite) + Opens Browser.
Uses port 5000 to avoid conflicts with port 3000/3001/3002.
Avoids batch/powershell parsing errors entirely.
"""
import subprocess
import sys
import time
import os
import urllib.request
import webbrowser

PROJECT_DIR = r"C:\Users\lokha\nexus-ai-safety"
BACKEND_DIR = os.path.join(PROJECT_DIR, "backend")
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")


def start_backend():
    """Start the FastAPI backend server on port 8000."""
    print("=" * 60)
    print("NEXUS AI SAFETY RESEARCH PLATFORM")
    print("=" * 60)
    print()
    print("[1/4] Starting Backend API (FastAPI + Uvicorn)...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Wait and verify it's running
    for _ in range(25):
        time.sleep(1)
        try:
            r = urllib.request.urlopen('http://localhost:8000/docs', timeout=3)
            print("  Backend API running on http://localhost:8000")
            return proc
        except Exception:
            continue
    print("  Backend starting... check console output")
    return proc


def start_frontend():
    """Start the React Vite frontend dashboard on port 5000."""
    print()
    print("[2/4] Starting Frontend Dashboard (React + Vite on port 5000)...")
    node_exe = r"C:\Program Files\nodejs\node.exe"
    if not os.path.exists(node_exe):
        print("  Node.js not found at expected path")
        print("  Frontend skipped - use browser at http://localhost:8000/docs")
        return None

    proc = subprocess.Popen(
        [node_exe, "vite", "--host", "--port", "5000"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for Vite to be ready
    for i in range(35):
        time.sleep(1)
        try:
            r = urllib.request.urlopen('http://localhost:5000', timeout=2)
            print("  Frontend Dashboard running on http://localhost:5000")
            return proc
        except Exception:
            if i >= 20:
                print(f"  Vite compiling... ({i+1}/35)")
            continue

    print("  Frontend still starting... check console window")
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
    print("  Dashboard:      http://localhost:5000")
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
    print("Opening dashboard in browser...")
    
    # Open default browser to dashboard
    try:
        webbrowser.open('http://localhost:5000')
        print("  Browser opened to http://localhost:5000")
    except Exception:
        print("  Could not auto-open browser - open manually at http://localhost:5000")

    print()
    print("Press CTRL+C to stop. Services continue in background.")
    print()

    # Keep alive and monitor
    try:
        while True:
            time.sleep(5)
            try:
                r = urllib.request.urlopen('http://localhost:8000/api/health', timeout=2)
            except:
                pass
            try:
                r = urllib.request.urlopen('http://localhost:5000', timeout=2)
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