$WshShell = New-Object -ComObject WScript.Shell

# Get actual Desktop path (handles OneDrive)
$DesktopPath = [Environment]::GetFolderPath("Desktop")
Write-Host "Using Desktop: $DesktopPath"

# Start shortcut - points to the renamed launch-nexus.bat
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\Nexus AI Safety Platform.lnk")
$Shortcut.TargetPath = 'cmd.exe'
$Shortcut.Arguments = '/c "C:\Users\lokha\nexus-ai-safety\launch-nexus.bat"'
$Shortcut.WorkingDirectory = "C:\Users\lokha\nexus-ai-safety\"
$Shortcut.Description = 'Nexus AI Safety Research Platform - One-click launcher'
$Shortcut.IconLocation = 'C:\Windows\System32\shell32.dll,13'
$Shortcut.Save()
Write-Host '✓ Start shortcut created: Nexus AI Safety Platform.lnk'

# Stop shortcut
$Shortcut2 = $WshShell.CreateShortcut("$DesktopPath\Stop Nexus.lnk")
$Shortcut2.TargetPath = 'cmd.exe'
$Shortcut2.Arguments = '/c "C:\Users\lokha\nexus-ai-safety\stop-nexus.bat"'
$Shortcut2.WorkingDirectory = "C:\Users\lokha\nexus-ai-safety\"
$Shortcut2.Description = 'Stop Nexus AI Safety Research Platform'
$Shortcut2.IconLocation = 'C:\Windows\System32\shell32.dll,27'
$Shortcut2.Save()
Write-Host '✓ Stop shortcut created: Stop Nexus.lnk'

Write-Host ""
Write-Host "✅ Done! Check your Desktop for the shortcuts."