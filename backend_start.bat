@echo off
title Nexus AI Safety Platform - Backend Only
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
echo   Backend API Service Starting...
echo   ============================================================
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%backend"

echo Starting FastAPI backend on port 8000...
C:\Users\lokha\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo BACKEND RUNNING - Port 8000
echo.
echo Access URLs:
echo   API:      http://localhost:8000
echo   Docs:     http://localhost:8000/docs
echo.
echo Features:
echo   • 10-15 Teenage Personas with OCEAN Personalities
echo   • Free Will & Autonomous Decision Making
echo   • Evolving Relationships
echo   • Hybrid LLM: Local Gemma 4 + Gemini 3.6 Flash
echo   • YAML Experiment Configs + PDF Reports
echo.
echo To stop: Close this window (services continue in background).
echo.
pause >NUL