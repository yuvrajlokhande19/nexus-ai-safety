@echo off
title Nexus AI Safety - Minimal Backend
color 0A

echo.
echo  Starting Minimal Nexus Backend...
echo   Port: 8000
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%backend"

echo Starting minimal FastAPI server...
C:\Users\lokha\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe -c "
import sys
sys.path.insert(0, '.')
from fastapi import FastAPI
app = FastAPI()

@app.get('/')
def root():
    return {'status': 'ok', 'message': 'Nexus Backend API'}

@app.get('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
" > minimal_app.py

C:\Users\lokha\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe -m uvicorn minimal_app:app --host 0.0.0.0 --port 8000 --reload