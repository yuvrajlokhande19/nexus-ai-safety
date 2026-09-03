#!/usr/bin/env python
import sys
sys.path.insert(0, r'C:\Users\lokha\nexus-ai-safety\backend')

# Install required packages first
import subprocess
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'ollama', 'google-generativeai', '-q'])

from app.main import app
print("✅ Backend imports successful!")
print(f"✅ App title: {app.title}")
print(f"✅ FastAPI version ready")