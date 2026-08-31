@echo off
title Stopping Nexus AI Safety Platform
color 0C

echo.
echo  Stopping Nexus AI Safety Research Platform...
echo  ==============================================
echo.

echo [1/4] Stopping Frontend...
taskkill /F /FI "WINDOWTITLE eq Nexus Frontend*" >NUL 2>&1
taskkill /F /IM node.exe /FI "COMMANDLINE eq *vite*" >NUL 2>&1
echo [OK] Frontend stopped

echo [2/4] Stopping Backend...
taskkill /F /FI "WINDOWTITLE eq Nexus Backend*" >NUL 2>&1
taskkill /F /FI "COMMANDLINE eq *uvicorn*app.main*" >NUL 2>&1
echo [OK] Backend stopped

echo [3/4] Stopping ChromaDB container...
docker stop chromadb >NUL 2>&1
echo [OK] ChromaDB stopped

echo [4/4] Stopping Ollama (optional - keeps model loaded for faster restart)...
REM Uncomment next line if you want to stop Ollama too:
REM taskkill /F /IM ollama.exe >NUL 2>&1
echo [SKIP] Ollama kept running (for faster restarts)

echo.
echo  ✅ All Nexus services stopped!
echo.
pause