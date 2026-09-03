@echo off
title Nexus AI Safety - Minimal Working Backend
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
echo   Minimal Backend Starting...
echo   (Using Ollama local model only)
echo   ============================================================
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%backend"

echo Starting backend with Ollama...
C:\Users\lokha\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe -c "
import subprocess
result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
print('Ollama models:')
print(result.stdout)
print()
print('Backend starting...')
" 

C:\Users\lokha\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload