@echo off
title Nexus AI Safety Research Platform
color 0A

echo.
echo ███╗   ███╗ █████╗ ██████╗ ██████╗ ███████╗██████╗ 
echo ████╗ ████║██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
echo ██╔████╔██║███████║██████╔╝██████╔╝█████╗  ██████╔╝
echo ██║╚██╔╝██║██╔══██║██╔══██╗██╔═══╝ ██╔═══╝ ██╔══██╗
echo ██║ ╚═╝ ██║██║  ██║██║  ██║██║     ███████╗██║  ██║
echo ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
echo.
echo   AI Safety Research Platform - Multi-Agent Persona System
echo   ============================================================
echo.

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

echo [1/6] Checking environment...
if not exist "backend\.env" (
    echo [ERROR] backend\.env not found!
    echo Please copy backend\.env.example to backend\.env and add your API keys
    pause
    exit /b 1
)

echo [2/6] Starting Ollama (local LLM)...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Ollama already running
) else (
    start "Ollama" /MIN ollama serve
    echo [WAIT] Waiting for Ollama to start...
    timeout /t 5 /nobreak >NUL
)

echo [3/6] Checking Gemma 4 model...
ollama list | find "gemma4:latest" >NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Gemma 4 model available
) else (
    echo [WARN] Gemma 4 not found - you may need to run: ollama pull gemma4:latest
)

echo [4/6] Starting ChromaDB (vector memory)...
docker ps --filter "name=chromadb" --format "{{.Names}}" | find "chromadb" >NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] ChromaDB already running
) else (
    docker start chromadb 2>NUL || (
        echo [INFO] Starting new ChromaDB container...
        docker run -d --name chromadb -p 8001:8000 chromadb/chroma:latest
    )
    echo [WAIT] Waiting for ChromaDB...
    timeout /t 3 /nobreak >NUL
)

echo [5/6] Starting Backend API (FastAPI)...
start "Nexus Backend" cmd /k "cd /d "%PROJECT_DIR%backend" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >NUL

echo [6/6] Starting Frontend (React + Vite)...
start "Nexus Frontend" cmd /k "cd /d "%PROJECT_DIR%frontend" && npm run dev"
timeout /t 3 /nobreak >NUL

echo.
echo ============================================================
echo  ✅ NEXUS IS STARTING!
echo ============================================================
echo.
echo  Frontend:  http://localhost:3000
echo  Backend:   http://localhost:8000
echo  API Docs:  http://localhost:8000/docs
echo.
echo  Press any key to open the dashboard in your browser...
pause >NUL

start "" "http://localhost:3000"

echo.
echo Nexus is running in the background.
echo Close this window when you're done (services will keep running).
echo To stop everything, run: stop-nexus.bat
echo.
pause