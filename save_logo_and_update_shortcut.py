"""
Script to save the logo image and update the desktop shortcut icon
"""
import os
import base64
from PIL import Image
import io

# The logo image in base64 (you'll need to save the image first)
# For now, we'll use the existing icon or create a placeholder

def update_shortcut_icon():
    """Update the desktop shortcut to use the new logo"""
    import subprocess
    
    # PowerShell script to update shortcut icon
    ps_script = """
    $WshShell = New-Object -ComObject WScript.Shell
    $DesktopPath = [System.Environment]::GetFolderPath('Desktop')
    $ShortcutPath = Join-Path $DesktopPath "DED Application.lnk"
    
    if (Test-Path $ShortcutPath) {
        $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
        $iconPath = "C:\\Users\\DELL\\DED\\assets\\calcatta_logo.ico"
        
        if (Test-Path $iconPath) {
            $Shortcut.IconLocation = $iconPath
            $Shortcut.Save()
            Write-Host "✅ تم تحديث أيقونة الاختصار بنجاح!" -ForegroundColor Green
        } else {
            Write-Host "⚠️ ملف الأيقونة غير موجود: $iconPath" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ الاختصار غير موجود على سطح المكتب" -ForegroundColor Red
    }
    """
    
    # Execute PowerShell script
    result = subprocess.run(
        ['powershell', '-Command', ps_script],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

if __name__ == "__main__":
    print("🔄 جاري تحديث أيقونة الاختصار...")
    update_shortcut_icon()
    print("\n✅ تم الانتهاء!")
    print("\n📝 ملاحظة: يرجى حفظ صورة الشعار في المسار:")
    print("   C:\\Users\\DELL\\DED\\assets\\calcatta_logo.ico")
    print("\nيمكنك استخدام أي أداة لتحويل الصورة PNG إلى ICO")

