"""
تحديث أيقونة التطبيق بشعار Calcatta الجديد
"""
from PIL import Image
import os

# مسار الصورة الجديدة (سيتم حفظها يدوياً)
logo_path = "assets/calcatta_logo.png"
icon_path = "assets/app_icon.ico"

print("📝 ملاحظة: يرجى حفظ صورة الشعار في المسار التالي:")
print(f"   {os.path.abspath(logo_path)}")
print()

if os.path.exists(logo_path):
    # فتح الصورة
    img = Image.open(logo_path)
    
    # تحويل إلى RGBA إذا لزم الأمر
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # إنشاء أحجام مختلفة للأيقونة
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # حفظ كملف .ico
    img.save(icon_path, format='ICO', sizes=icon_sizes)
    
    print(f"✅ تم إنشاء الأيقونة بنجاح: {icon_path}")
    
    # تحديث الاختصار
    print("\n🔄 تحديث الاختصار على سطح المكتب...")
    os.system('powershell -ExecutionPolicy Bypass -File create_shortcut.ps1')
    
else:
    print(f"❌ لم يتم العثور على الصورة في: {logo_path}")
    print("\nيرجى:")
    print("1. حفظ صورة الشعار في المسار أعلاه")
    print("2. تشغيل هذا السكريبت مرة أخرى")

