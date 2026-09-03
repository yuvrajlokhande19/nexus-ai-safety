@echo off
title Nexus AI Safety - Working Backend
color 0A

echo.
echo  ███╗   ███╗ █████╗ ██████╗ ███████╗██████╗ 
echo  ████╗ ████║██╔══██╗██╔══██╗██╔════╝██╔══██╗
echo  ██╔████╔██║███████║██████╔╝█████╗  ██████╔╝
echo  ██║╚██╔╝██║██╔══██║██╔═══╝ ██╔═══╝ ██══██╗
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
echo [2/3] Starting Minimal FastAPI Backend (NO Google packages)...
C:\Users\lokha\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe -c "
import sys
sys.path.insert(0, '.')
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title='Nexus Minimal')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
def root():
    return {'status': 'ok', 'service': 'Nexus Minimal Backend'}

@app.get('/health')
def health():
    return {'status': 'healthy', 'model': 'ollama-local'}

@app.get('/personas')
def personas():
    return {'personas': [], 'count': 0}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
" > minimal_app.py

C:\Users\lokha\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe -m uvicorn minimal_app:app --host 0.0.0.0 --port 8000 --reload