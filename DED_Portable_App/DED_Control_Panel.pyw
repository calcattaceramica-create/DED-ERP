import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import webbrowser
import sys
import os
from pathlib import Path
import sqlite3
from werkzeug.security import generate_password_hash

class DEDControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 DED Control Panel - لوحة التحكم")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.root.minsize(700, 500)

        # Modern Light Theme Colors
        self.colors = {
            'bg': '#f8fafc',
            'bg_light': '#ffffff',
            'card': '#ffffff',
            'accent': '#3b82f6',
            'accent_hover': '#2563eb',
            'success': '#22c55e',
            'success_hover': '#16a34a',
            'danger': '#ef4444',
            'danger_hover': '#dc2626',
            'text': '#1e293b',
            'text_gray': '#64748b',
            'border': '#e2e8f0',
        }

        self.root.configure(bg=self.colors['bg'])

        # App directory
        if getattr(sys, 'frozen', False):
            self.app_dir = Path(sys.executable).parent
        else:
            self.app_dir = Path(__file__).parent

        # Flask process
        self.flask_process = None
        self.is_running = False

        # Build UI
        self.create_ui()
        self.center_window()

        # Check status
        self.root.after(500, self.check_status)

        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_ui(self):
        # Main container
        main = tk.Frame(self.root, bg=self.colors['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        header = tk.Frame(main, bg=self.colors['bg'])
        header.pack(fill=tk.X, pady=(0, 20))

        title = tk.Label(
            header,
            text="🚀 DED Control Panel",
            font=("Segoe UI", 24, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title.pack()

        subtitle = tk.Label(
            header,
            text="لوحة التحكم في نظام DED",
            font=("Segoe UI", 12),
            bg=self.colors['bg'],
            fg=self.colors['text_gray']
        )
        subtitle.pack()

        # Status Card
        status_card = tk.Frame(main, bg=self.colors['card'], relief=tk.FLAT, bd=0)
        status_card.pack(fill=tk.X, pady=(0, 20))

        status_inner = tk.Frame(status_card, bg=self.colors['card'])
        status_inner.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            status_inner,
            text="حالة التطبيق - Application Status",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(pady=(0, 10))

        self.status_label = tk.Label(
            status_inner,
            text="⚫ غير مشغّل - Not Running",
            font=("Segoe UI", 16, "bold"),
            bg=self.colors['card'],
            fg=self.colors['danger']
        )
        self.status_label.pack()

        # Control Buttons
        btn_frame = tk.Frame(main, bg=self.colors['bg'])
        btn_frame.pack(fill=tk.X, pady=(0, 20))

        # Start Button
        self.start_btn = tk.Button(
            btn_frame,
            text="▶️ تشغيل التطبيق\nStart Application",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['success'],
            fg='white',
            activebackground=self.colors['success_hover'],
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.start_app,
            height=3
        )
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # Stop Button
        self.stop_btn = tk.Button(
            btn_frame,
            text="⏹️ إيقاف التطبيق\nStop Application",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['danger'],
            fg='white',
            activebackground=self.colors['danger_hover'],
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.stop_app,
            height=3
        )
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Browser Button
        browser_btn = tk.Button(
            main,
            text="🌐 فتح المتصفح\nOpen Browser",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['accent'],
            fg='white',
            activebackground=self.colors['accent_hover'],
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.open_browser,
            height=2
        )
        browser_btn.pack(fill=tk.X, pady=(0, 20))

        # Database Tools
        db_card = tk.Frame(main, bg=self.colors['card'], relief=tk.FLAT, bd=0)
        db_card.pack(fill=tk.BOTH, expand=True)

        db_inner = tk.Frame(db_card, bg=self.colors['card'])
        db_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            db_inner,
            text="أدوات قاعدة البيانات - Database Tools",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(pady=(0, 10))

        # Reset Admin Password Button
        reset_btn = tk.Button(
            db_inner,
            text="🔑 إعادة تعيين كلمة مرور المدير\nReset Admin Password",
            font=("Segoe UI", 11),
            bg=self.colors['card'],
            fg=self.colors['text'],
            relief=tk.SOLID,
            bd=1,
            cursor='hand2',
            command=self.reset_admin_password,
            height=2
        )
        reset_btn.pack(fill=tk.X, pady=5)

    def start_app(self):
        """Start the Flask application"""
        try:
            self.flask_process = subprocess.Popen(
                [sys.executable, "run.py"],
                cwd=self.app_dir,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            self.is_running = True
            self.update_status()
            messagebox.showinfo("نجح - Success", "تم تشغيل التطبيق!\nApplication started!")
        except Exception as e:
            messagebox.showerror("خطأ - Error", f"فشل تشغيل التطبيق:\n{str(e)}")

    def stop_app(self):
        """Stop the Flask application"""
        if self.flask_process:
            try:
                self.flask_process.terminate()
                self.flask_process.wait(timeout=5)
            except:
                try:
                    self.flask_process.kill()
                except:
                    pass

        self.is_running = False
        self.update_status()
        messagebox.showinfo("نجح - Success", "تم إيقاف التطبيق!\nApplication stopped!")

    def open_browser(self):
        """Open browser to the application"""
        if not self.is_running:
            response = messagebox.askyesno(
                "تحذير - Warning",
                "⚠️ التطبيق غير مشغّل!\nApplication is not running!\n\n"
                "هل تريد تشغيله الآن؟\nDo you want to start it now?"
            )
            if response:
                self.start_app()
                self.root.after(2000, lambda: webbrowser.open("http://127.0.0.1:5000"))
            return

        webbrowser.open("http://127.0.0.1:5000")

    def check_status(self):
        """Check if Flask is running"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 5000))
            sock.close()

            if result == 0:
                self.is_running = True
            else:
                self.is_running = False
                if self.flask_process:
                    poll = self.flask_process.poll()
                    if poll is not None:
                        self.flask_process = None
        except:
            self.is_running = False

        self.update_status()
        self.root.after(2000, self.check_status)

    def update_status(self):
        """Update status display"""
        if self.is_running:
            self.status_label.config(
                text="🟢 مشغّل - Running",
                fg=self.colors['success']
            )
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.status_label.config(
                text="⚫ غير مشغّل - Not Running",
                fg=self.colors['danger']
            )
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def reset_admin_password(self):
        """Reset admin password in database"""
        db_path = self.app_dir / "instance" / "ded.db"

        if not db_path.exists():
            messagebox.showerror(
                "خطأ - Error",
                "قاعدة البيانات غير موجودة!\nDatabase not found!"
            )
            return

        new_password = "admin123"

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Update admin password
            hashed_password = generate_password_hash(new_password)
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE username = 'admin'",
                (hashed_password,)
            )

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "نجح - Success",
                f"تم إعادة تعيين كلمة المرور!\nPassword reset successfully!\n\n"
                f"Username: admin\nPassword: {new_password}"
            )
        except Exception as e:
            messagebox.showerror(
                "خطأ - Error",
                f"فشل إعادة تعيين كلمة المرور:\n{str(e)}"
            )

    def on_closing(self):
        """Handle window close event"""
        if self.is_running:
            response = messagebox.askyesnocancel(
                "تأكيد - Confirm",
                "التطبيق لا يزال يعمل!\nApplication is still running!\n\n"
                "هل تريد إيقافه قبل الإغلاق؟\nDo you want to stop it before closing?\n\n"
                "نعم = إيقاف وإغلاق | Yes = Stop & Close\n"
                "لا = إغلاق فقط | No = Close only\n"
                "إلغاء = العودة | Cancel = Go back"
            )

            if response is None:  # Cancel
                return
            elif response:  # Yes - Stop and close
                self.stop_app()

        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DEDControlPanel(root)
    root.mainloop()


