@echo off
title Nexus AI Safety Platform - Starting...
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
echo   Multi-Agent Persona System with Free Will Relationships
echo   ============================================================
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo [1/4] Starting Backend API (FastAPI + Uvicorn)...
cd /d "%PROJECT_DIR%backend"
C:\Program Files\nodejs\node.exe --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Node.js available for frontend
) else (
    echo [WARN] Node.js not found - frontend will be skipped
)

set "PYTHON_EXE=C:\Users\lokha\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe"
start "Nexus Backend API" cmd /k "cd /d "%PROJECT_DIR%backend" && %PYTHON_EXE% -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >NUL

echo [2/4] Backend starting... please wait.
timeout /t 5 /nobreak >NUL

echo [3/4] Starting Frontend Dashboard (React + Vite)...
cd /d "%PROJECT_DIR%frontend"
if not exist node_modules (
    echo [INSTALL] Installing frontend dependencies...
    npm install
) else (
    echo [OK] Frontend dependencies installed
)

start "Nexus Frontend" cmd /k "cd /d "%PROJECT_DIR%frontend" && npm run dev"
timeout /t 5 /nobreak >NUL

echo [4/4] Opening dashboard in browser...
start "" "http://localhost:3002"

echo.
echo ============================================================
echo  ✅ NEXUS AI SAFETY PLATFORM IS NOW RUNNING!
echo ============================================================
echo.
echo   📊 Dashboard:    http://localhost:3002
echo   🔧 Backend API:  http://localhost:8000
echo   📚 API Docs:     http://localhost:8000/docs
echo.
echo   Features Active:
echo   • 10-15 Teenage Personas with OCEAN Personalities
echo   • Free Will Autonomous Decision Making
echo   • Evolving Relationships (Friends/Rivals/Partners)
echo   • Private vs Public Belief Tracking (Deception Detection)
echo   • Real-time Neural Network Visualization
echo   • Hybrid LLM: Local Gemma 4 + Gemini 3.6 Flash (4 keys)
echo   • YAML Experiment Configs + PDF Reports
echo   • GitHub Integration for Resource Tracking
echo.
echo   Nexus is running in the background console windows.
echo.
echo   To STOP everything: Double-click "stop-nexus.bat" 
echo   (or run it from this folder)
echo.
echo   Press any key to close this launcher window...
echo   (Services will continue running in background)
pause >Nul