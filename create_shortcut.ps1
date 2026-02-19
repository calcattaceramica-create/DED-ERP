# Create Desktop Shortcut for DED Application (No Console Window)

Write-Host "Creating shortcut without console window..." -ForegroundColor Cyan
Write-Host ""

$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "DED Inventory System.lnk"
$VBSPath = "C:\Users\DELL\DED\start_ded_hidden.vbs"
$WorkingDirectory = "C:\Users\DELL\DED"

# Remove old shortcuts if exist
$oldShortcuts = @(
    (Join-Path $DesktopPath "DED Application.lnk"),
    (Join-Path $DesktopPath "DED ERP System.lnk"),
    (Join-Path $DesktopPath "DED Inventory System.lnk")
)

foreach ($oldShortcut in $oldShortcuts) {
    if (Test-Path $oldShortcut) {
        Remove-Item $oldShortcut -Force
        Write-Host "Removed old shortcut" -ForegroundColor Yellow
    }
}

# Create new shortcut using VBS launcher
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"$VBSPath`""
$Shortcut.WorkingDirectory = $WorkingDirectory
$Shortcut.Description = "DED Inventory & ERP System - Calcatta Ceramica"

# Set icon if exists
$iconPath = "C:\Users\DELL\DED\assets\app_icon.ico"
if (Test-Path $iconPath) {
    $Shortcut.IconLocation = $iconPath
    Write-Host "Icon set successfully" -ForegroundColor Green
}

$Shortcut.Save()

Write-Host ""
Write-Host "SUCCESS: Desktop shortcut created!" -ForegroundColor Green
Write-Host "Path: $ShortcutPath" -ForegroundColor Cyan
Write-Host "The app will now run without console window!" -ForegroundColor Green
Write-Host "Browser will open automatically" -ForegroundColor Yellow
Write-Host ""

