import webview
import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

def show_error_message(title, message):
    """
    عرض رسالة خطأ في نافذة منبثقة
    """
    try:
        root = tk.Tk()
        root.withdraw()  # إخفاء النافذة الرئيسية
        messagebox.showerror(title, message)
        root.destroy()
    except:
        # في حالة فشل tkinter، اطبع الرسالة فقط
        print(f"{title}: {message}")

def show_info_message(title, message):
    """
    عرض رسالة معلومات في نافذة منبثقة
    """
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(title, message)
        root.destroy()
    except:
        print(f"{title}: {message}")

def get_executable_path():
    """
    الحصول على مسار الملف التنفيذي أو ملف Python
    يعمل مع py2exe وغيره من المحولات
    """
    if getattr(sys, 'frozen', False):
        # إذا كان البرنامج محول لـ exe
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller
            return Path(sys.executable).parent
        else:
            # py2exe أو cx_Freeze
            return Path(sys.executable).parent
    else:
        # إذا كان يعمل كملف Python عادي
        return Path(__file__).parent.absolute()

def get_html_path():
    """
    الحصول على مسار ملف HTML بناءً على مكان الملف التنفيذي
    """
    # الحصول على مجلد الملف التنفيذي
    exe_dir = get_executable_path()
    
    # البحث عن main.html في مواقع مختلفة
    possible_paths = [
        exe_dir / "main.html",                        # في نفس مجلد exe
        exe_dir / "aihos" / "main.html",             # في مجلد aihos
        exe_dir / "html" / "main.html",              # في مجلد html
        exe_dir / "web" / "main.html",               # في مجلد web
        exe_dir / "src" / "main.html",               # في مجلد src
        exe_dir / "assets" / "main.html",            # في مجلد assets
        exe_dir / ".." / "main.html",                # في المجلد الأب
        exe_dir / ".." / "aihos" / "main.html",      # في مجلد aihos الأب
    ]
    
    # البحث عن الملف في المسارات المحددة
    for path in possible_paths:
        try:
            if path.exists() and path.is_file():
                return path.absolute()
        except:
            continue
    
    # البحث في جميع المجلدات الفرعية (بحث شامل)
    try:
        for html_file in exe_dir.rglob("main.html"):
            if html_file.is_file():
                return html_file.absolute()
    except:
        pass
    
    # البحث في المجلد الأب أيضاً
    try:
        parent_dir = exe_dir.parent
        for html_file in parent_dir.rglob("main.html"):
            if html_file.is_file():
                return html_file.absolute()
    except:
        pass
    
    return None

def create_desktop_app():
    """
    إنشاء تطبيق سطح مكتب من ملف HTML
    """
    
    # الحصول على مسار الملف التنفيذي للتشخيص
    exe_path = get_executable_path()
    
    # البحث عن ملف HTML
    html_path = get_html_path()
    
    if not html_path:
        # قائمة الملفات الموجودة للتشخيص
        try:
            files_list = []
            for item in exe_path.iterdir():
                files_list.append(f"{'📁' if item.is_dir() else '📄'} {item.name}")
            files_text = "\n".join(files_list[:10])  # أول 10 ملفات فقط
            if len(files_list) > 10:
                files_text += f"\n... و {len(files_list) - 10} ملف آخر"
        except:
            files_text = "لا يمكن قراءة محتويات المجلد"
        
        error_msg = f"""لم يتم العثور على ملف main.html

مسار البحث: {exe_path}

الملفات الموجودة:
{files_text}

تأكد من وضع ملف main.html في:
• نفس مجلد الملف التنفيذي
• مجلد فرعي يسمى 'aihos'
• أي مجلد فرعي آخر"""
        
        show_error_message("خطأ - ملف غير موجود", error_msg)
        return False
    
    # تحويل إلى file URL
    file_url = html_path.as_uri()
    
    try:        
        # إنشاء نافذة التطبيق
        webview.create_window(
            title="AIHOS - نظام التشغيل الذكي",
            url=file_url,
            width=1200,
            height=800,
            min_size=(800, 600),
            resizable=True,
            fullscreen=False,
            minimized=False,
            on_top=False,
            shadow=True,
            focus=True
        )
        
        # تشغيل التطبيق
        webview.start(debug=False)
        return True
        
    except Exception as e:
        error_msg = f"""خطأ في تشغيل التطبيق:
{str(e)}

مسار HTML المستخدم:
{html_path}

تأكد من:
• تثبيت pywebview: pip install pywebview
• صحة ملف HTML
• صلاحيات الوصول للملف"""
        show_error_message("خطأ في التشغيل", error_msg)
        return False

def check_dependencies():
    """
    التحقق من المكتبات المطلوبة
    """
    missing_libs = []
    
    try:
        import webview
    except ImportError:
        missing_libs.append("pywebview")
    
    if missing_libs:
        error_msg = f"""المكتبات التالية غير مثبتة:
{', '.join(missing_libs)}

لتثبيتها استخدم:
pip install {' '.join(missing_libs)}

ثم أعد تحويل البرنامج لـ exe"""
        
        show_error_message("مكتبات مفقودة", error_msg)
        return False
    
    return True

def main():
    """
    الدالة الرئيسية
    """
    # التحقق من المكتبات المطلوبة
    if not check_dependencies():
        return
    
    # تشغيل التطبيق
    success = create_desktop_app()
    
    if not success:
        # في حالة الفشل، انتظر قليلاً قبل الإغلاق
        import time
        time.sleep(2)

# دالة للتشخيص وإظهار معلومات النظام
def show_debug_info():
    """
    إظهار معلومات التشخيص
    """
    exe_path = get_executable_path()
    html_path = get_html_path()
    
    debug_info = f"""معلومات التشخيص:

مسار التنفيذ: {exe_path}
حالة النظام: {'exe محول' if getattr(sys, 'frozen', False) else 'Python عادي'}
ملف HTML: {html_path if html_path else 'غير موجود'}

sys.executable: {sys.executable}
sys.argv[0]: {sys.argv[0]}
sys.frozen: {getattr(sys, 'frozen', 'False')}
"""
    
    show_info_message("معلومات التشخيص", debug_info)

if __name__ == "__main__":
    # لإظهار معلومات التشخيص، قم بإلغاء التعليق عن السطر التالي:
    # show_debug_info()
    
    main()