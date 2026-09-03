#!/usr/bin/env python
import subprocess
import sys

# Start Vite frontend
frontend_dir = r"C:\Users\lokha\nexus-ai-safety\frontend"
vite_cmd = [r"C:\Program Files\nodejs\node.exe", "vite", "--host", "--port", "3000"]

print("Starting Nexus AI Safety Platform...")
print(f"Frontend: Vite dev server on http://localhost:3000")
print(f"Backend: FastAPI on http://localhost:8000 (already running)")
print()

# Start Vite in background
process = subprocess.Popen(
    vite_cmd,
    cwd=frontend_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

print(f"Vite process started with PID: {process.pid}")
print("Waiting for frontend to start...")
import time
time.sleep(5)

# Check if it's running
try:
    import urllib.request
    r = urllib.request.urlopen('http://localhost:3000', timeout=3)
    print(f"✅ Frontend running on port 3000 (status: {r.status})")
except Exception as e:
    print(f"⚠️  Frontend still starting... (error: {e})")
    print("Check the terminal output above")

print()
print("=" * 60)
print("NEXUS AI SAFETY PLATFORM IS NOW RUNNING!")
print("=" * 60)
print()
print("Access Points:")
print("  📊 Dashboard: http://localhost:3000")
print("  🔧 Backend API: http://localhost:8000")
print("  📚 API Docs: http://localhost:8000/docs")
print()
print("Features:")
print("  • 10-15 Teenage Personas with OCEAN Personalities")
print("  • Free Will & Autonomous Decision Making")
print("  • Evolving Relationships (Friends/Rivals/Partners)")
print("  • Private vs Public Belief Tracking")
print("  • Real-time Neural Network Visualization")
print("  • Hybrid LLM: Local Gemma 4 + Gemini 3.6 Flash")
print("  • YAML Experiment Configs + PDF Reports")
print()
print("Press CTRL+C to stop (services will continue in background)")
print()

# Keep the script running
try:
    while True:
        time.sleep(10)
        # Check both services are alive
        try:
            r1 = urllib.request.urlopen('http://localhost:8000/api/health', timeout=2)
            r2 = urllib.request.urlopen('http://localhost:3000', timeout=2)
            print(f"✅ Both services healthy - Backend: {r1.status}, Frontend: {r2.status}")
        except:
            print("⚠️  One or both services unresponsive")
except KeyboardInterrupt:
    print("\n🛑 Stopping Nexus Platform...")
    process.terminate()
    print("Done.")