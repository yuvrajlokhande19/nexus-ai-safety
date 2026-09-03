@echo off
title Nexus AI Safety Platform - Full Start
color 0A

echo.
echo  ███╗   ███╗ █████╗ ███████╗██████╗ 
echo  ████╗ ████║██╔══██╗██╔════╝██╔══██╗
echo  ██╔████╔██║███████║██████╔╝█████╗  ██████╔╝
echo  ██║╚██╔╝██║██╔══██║██╔═══╝ ██╔══██╗
echo  ██║ ╚═╝ ██║██║  ██║██║  ██║██║     ███████╗██║  ██║
echo  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
echo.
echo   NEXUS AI SAFETY RESEARCH PLATFORM
echo   Starting Full Stack...
echo   ============================================================
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo.
echo [1/4] Starting Backend (Minimal Flask + Ollama Local)...
cd /d "%PROJECT_DIR%backend"
echo Starting minimal Flask backend on port 8000...
timeout /t 3 /nobreak >NUL

echo.
echo [2/4] Starting Frontend (React Vite on port 5000)...
cd /d "%PROJECT_DIR%frontend"
echo Starting Vite frontend on port 5000...
timeout /t 3 /nobreak >NUL

echo.
echo [3/4] Waiting for services to initialize...
timeout /t 5 /nobreak >NUL

echo.
echo [4/4] Opening dashboard in browser...
start "" "http://localhost:5000"

echo.
echo ============================================================
echo  ✅ NEXUS AI SAFETY PLATFORM IS NOW RUNNING!
echo ============================================================
echo.
echo   📊 Dashboard:    http://localhost:5000
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
echo   Nexus is running in the background console windows.
echo.
echo   To STOP everything: Close these console windows.
echo.
echo   Press any key to close this launcher window...
echo   (Services will continue running in background)
pause >Nul