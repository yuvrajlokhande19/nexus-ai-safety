@echo off
title Nexus AI Safety Platform - Starting Backend
color 0A

echo.
echo  ███╗   ███╗ █████╗ ██████╗ ███████╗██████╗ 
echo  ████╗ ████║██╔══██╗██╔══██╗██╔════╝██╔══██╗
echo  ██╔████╔██║███████║██████╔╝█████╗  █████╗  ██████╔╝
echo  ██║╚██╔╝██║██╔══██║██╔══██╗██╔═══╝ ██══██╗
echo  ██║ ╚═╝ ██║██║  ██║██║  ██║██║     ███████╗██║  ██║
echo  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
echo.
echo   NEXUS AI SAFETY RESEARCH PLATFORM
echo   Multi-Agent Persona System with Free Will & Relationships
echo   ============================================================
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%backend"

echo Starting Backend API (FastAPI + Uvicorn)...
C:\Users\lokha\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo Backend started on http://localhost:8000
echo API Docs on http://localhost:8000/docs
echo.
echo Press CTRL+C to stop. Services will continue in background.

pause >NUL