@echo off
REM Install Nexus AI Safety Platform Desktop Shortcut

title Install Nexus Desktop Shortcut
color 0B

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║  Nexus AI Safety Platform - Desktop Shortcut Installer  ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

set "PROJECT_DIR=%~dp0"
set "SHORTCUT_NAME=Nexus AI Safety Platform"
set "LAUNCHER=%PROJECT_DIR%LAUNCH NEXUS.bat"

echo Project folder: %PROJECT_DIR%
echo.

if not exist "%LAUNCHER%" (
    echo [ERROR] Launcher not found: %LAUNCHER%
    pause
    exit /b 1
)

echo Creating PowerShell script for shortcut creation...

set "PS_SCRIPT=%TEMP%\nexus_create_shortcuts.ps1"

(
echo $WshShell = New-Object -ComObject WScript.Shell
echo $DesktopPath = [Environment]::GetFolderPath("Desktop")
echo Write-Host "Using Desktop: $DesktopPath"
echo.
echo $Shortcut = $WshShell.CreateShortcut("$DesktopPath\Nexus AI Safety Platform.lnk")
echo $Shortcut.TargetPath = 'cmd.exe'
echo $Shortcut.Arguments = '/c "%LAUNCHER%"'
echo $Shortcut.WorkingDirectory = "%PROJECT_DIR%"
echo $Shortcut.Description = 'Nexus AI Safety Research Platform - One-click launcher'
echo $Shortcut.IconLocation = '%SystemRoot%\System32\shell32.dll,13'
echo $Shortcut.Save()
echo Write-Host 'Start shortcut created'
echo.
echo $Shortcut2 = $WshShell.CreateShortcut("$DesktopPath\Stop Nexus.lnk")
echo $Shortcut2.TargetPath = 'cmd.exe'
echo $Shortcut2.Arguments = '/c "%PROJECT_DIR%stop-nexus.bat"'
echo $Shortcut2.WorkingDirectory = "%PROJECT_DIR%"
echo $Shortcut2.Description = 'Stop Nexus AI Safety Research Platform'
echo $Shortcut2.IconLocation = '%SystemRoot%\System32\shell32.dll,27'
echo $Shortcut2.Save()
echo Write-Host 'Stop shortcut created'
) > "%PS_SCRIPT%"

echo Running PowerShell to create shortcuts...
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%"

if errorlevel 1 (
    echo [ERROR] Failed to create shortcuts
    pause
    exit /b 1
)

del "%PS_SCRIPT%"

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  ✅ INSTALLATION COMPLETE!                               ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║  Two shortcuts created on your Desktop:                  ║
echo ║                                                            ║
echo ║    🟢 "Nexus AI Safety Platform"  - STARTS everything    ║
echo ║    🔴 "Stop Nexus"              - STOPS everything       ║
echo ║                                                            ║
echo ║  Just DOUBLE-CLICK the green one to launch!              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
pause