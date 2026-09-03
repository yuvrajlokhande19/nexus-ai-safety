@echo off
cd C:\Users\lokha\nexus-ai-safety\backend
C:\Users\lokha\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1
echo Backend started - check backend.log