@echo off
setlocal enabledelayedexpansion
REM Nexus AI Safety Platform - One-Click Launcher (Robust Version)

title Nexus AI Safety Research Platform - Starting...
color 0A

echo.
echo  ███╗   ███╗ █████╗ ██████╗ ██████╗ ███████╗██████╗ 
echo  ████╗ ████║██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
echo  ██╔████╔██║███████║██████╔╝██████╔╝█████╗  ██████╔╝
echo  ██║╚██╔╝██║██╔══██║██╔══██╗██╔═══╝ ██╔═══╝ ██══██╗
echo  ██║ ╚═╝ ██║██║  ██║██║  ██║██║     ███████╗██║  ██║
echo  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
echo.
echo   NEXUS AI SAFETY RESEARCH PLATFORM
echo   Multi-Agent Persona System with Free Will & Relationships
echo   ============================================================
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo [1/7] Checking environment configuration...
if not exist "backend\.env" (
    echo.
    echo [ERROR] backend\.env not found!
    echo.
    echo Please copy backend\.env.example to backend\.env and add your 4 Gemini API keys.
    echo.
    pause
    exit /b 1
)
echo [OK] Environment configured

echo [2/7] Checking Ollama service...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "!ERRORLEVEL!"=="0" (
    echo [OK] Ollama already running
) else (
    echo [START] Launching Ollama...
    start "Ollama Server" /MIN ollama serve
    echo [WAIT] Waiting for Ollama to initialize...
    timeout /t 5 /nobreak >NUL
)

echo [3/7] Checking Gemma 4 model...
ollama list 2>NUL | findstr /I "gemma4:latest" >NUL
if "!ERRORLEVEL!"=="0" (
    echo [OK] Gemma 4 model ready (9.6 GB)
) else (
    echo [DOWNLOAD] Gemma 4 not found - downloading (this may take a while)...
    ollama pull gemma4:latest
)

echo [4/7] Local memory store initialized...
echo [OK] Using file-based vector memory (no Docker required)

echo [5/7] Starting Backend API (FastAPI + WebSocket)...
set "PYTHON_EXE=C:\Users\lokha\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe"
start "Nexus Backend API" cmd /k "cd /d "%PROJECT_DIR%backend" && "%PYTHON_EXE%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo [WAIT] Backend initializing...
timeout /t 5 /nobreak >NUL

echo [6/7] Checking Frontend dependencies...
if not exist "frontend\node_modules" (
    echo [INSTALL] Installing frontend dependencies (first run)...
    cd /d "%PROJECT_DIR%frontend" && npm install
    cd /d "%PROJECT_DIR%"
) else (
    echo [OK] Frontend dependencies installed
)

echo [7/7] Starting Frontend Dashboard (React + Vite)...
start "Nexus Frontend" cmd /k "cd /d "%PROJECT_DIR%frontend" && npm run dev"
echo [WAIT] Frontend compiling...
timeout /t 8 /nobreak >NUL

echo.
echo ============================================================
echo  ✅ NEXUS AI SAFETY PLATFORM IS NOW RUNNING!
echo ============================================================
echo.
echo   📊 Dashboard:    http://localhost:3000
echo   🔧 Backend API:  http://localhost:8000
echo   📚 API Docs:     http://localhost:8000/docs
echo.
echo   Features Active:
echo   • 10-15 Teenage Personas with OCEAN Personalities
echo   • Free Will & Autonomous Decision Making
echo   • Evolving Relationships (Friends/Rivals/Partners)
echo   • Private vs Public Belief Tracking (Deception Detection)
echo   • Real-time Neural Network Visualization
echo   • Hybrid LLM: Local Gemma 4 + Gemini 3.6 Flash (4 keys)
echo   • YAML Experiment Configs + PDF Reports
echo   • GitHub Integration for Resource Tracking
echo.
echo   Opening dashboard in browser...
start "" "http://localhost:3000"

echo.
echo ============================================================
echo   Nexus is running in the background console windows.
echo ============================================================
echo.
echo   To STOP everything: Double-click "stop-nexus.bat" 
echo   (or run it from this folder)
echo.
echo   Press any key to close this launcher window...
echo   (Services will continue running in background)
pause >NUL