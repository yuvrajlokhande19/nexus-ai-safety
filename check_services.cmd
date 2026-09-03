@echo off
chcp 65001 >NUL
echo.
echo Checking Nexus Services...
echo.

REM Check Backend (port 8000)
echo [1/2] Checking Backend API (port 8000)...
curl -s -o /dev/null -w "HTTP Status: %{{http_code}}" http://localhost:8000/api/health 2>NUL | find "200" >NUL
if %errorlevel%==0 (
    echo [OK] Backend API running on http://localhost:8000
) else (
    echo [FAIL] Backend API NOT running on port 8000
)

REM Check Frontend (port 3000)
echo.
echo [2/2] Checking Frontend Dashboard (port 3000)...
curl -s -o /dev/null -w "HTTP Status: %{{http_code}}" http://localhost:3000 2>NUL | find "200" >NUL
if %errorlevel%==0 (
    echo [OK] Frontend Dashboard running on http://localhost:3000
) else (
    echo [FAIL] Frontend Dashboard NOT running on port 3000
    echo   Starting frontend...
    cd /d "%~dp0frontend"
    start "" npm run dev
    echo [WAIT] Frontend starting...
    timeout /t 10 /nobreak >NUL
)

echo.
echo ============================================================
echo Nexus Service Check Complete
echo ============================================================