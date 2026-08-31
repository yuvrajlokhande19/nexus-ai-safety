<# 
.SYNOPSIS
    Creates a desktop shortcut for Nexus AI Safety Research Platform
.DESCRIPTION
    Creates a one-click launcher on your Desktop that starts the entire Nexus system
#>

param(
    [string]$ProjectPath = "C:\Users\lokha\nexus-ai-safety",
    [string]$ShortcutName = "Nexus AI Safety Platform"
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Creating Desktop Shortcut for Nexus AI Safety Platform" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verify project exists
if (-not (Test-Path $ProjectPath)) {
    Write-Host "[ERROR] Project not found at: $ProjectPath" -ForegroundColor Red
    Write-Host "Please update the \$ProjectPath variable in this script." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "$ProjectPath\start-nexus.bat")) {
    Write-Host "[ERROR] start-nexus.bat not found in project directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Get Desktop path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "$ShortcutName.lnk"

Write-Host "[1/4] Creating shortcut at: $ShortcutPath" -ForegroundColor Green

# Create shortcut using WScript.Shell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "cmd.exe"
$Shortcut.Arguments = "/c `"$ProjectPath\start-nexus.bat`""
$Shortcut.WorkingDirectory = $ProjectPath
$Shortcut.Description = "Nexus AI Safety Research Platform - Multi-Agent Persona System"
$Shortcut.IconLocation = "$ProjectPath\assets\nexus.ico,0"  # Will use default if not found
$Shortcut.Save()

Write-Host "[2/4] Shortcut created successfully!" -ForegroundColor Green

# Also create a stop shortcut
$StopShortcutPath = Join-Path $DesktopPath "Stop Nexus.lnk"
$StopShortcut = $WshShell.CreateShortcut($StopShortcutPath)
$StopShortcut.TargetPath = "cmd.exe"
$StopShortcut.Arguments = "/c `"$ProjectPath\stop-nexus.bat`""
$StopShortcut.WorkingDirectory = $ProjectPath
$StopShortcut.Description = "Stop Nexus AI Safety Research Platform"
$StopShortcut.Save()

Write-Host "[3/4] Stop shortcut created: $StopShortcutPath" -ForegroundColor Green

# Verify
if (Test-Path $ShortcutPath) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "  ✅ DONE! Two shortcuts created on your Desktop:" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "     • $ShortcutName.lnk     - Starts the full system" -ForegroundColor White
    Write-Host "     • Stop Nexus.lnk        - Stops all services" -ForegroundColor White
    Write-Host ""
    Write-Host "  Just double-click '$ShortcutName' to launch Nexus!" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "[ERROR] Failed to create shortcut" -ForegroundColor Red
}

Read-Host "Press Enter to close"