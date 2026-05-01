$WshShell = New-Object -comObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\Smart Attendance Admin.lnk")
$Shortcut.TargetPath = "$PWD\run_admin_panel.vbs"
$Shortcut.IconLocation = "$PWD\assets\icon.ico"
$Shortcut.WorkingDirectory = "$PWD"
$Shortcut.Save()
Write-Host "Shortcut created on Desktop"
