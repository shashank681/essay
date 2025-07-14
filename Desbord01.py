import customtkinter as ctk 
import tkinter as tk
import os
import sys
import subprocess
import time
from datetime import datetime, timedelta

# === SETUP ===
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# === BASE PATHS ===
BASE_DIR = os.path.join("C:", "new 12", "New folder")
PAGES_DIR = os.path.join(BASE_DIR, "odd", "Pages")
DASHBOARD_DIR = os.path.join(BASE_DIR, "odd", "Deshbord")

ICON_PATH = os.path.join(PAGES_DIR, "easysell.ico")
WELCOME_IMAGE_PATH = os.path.join(PAGES_DIR, "well come.png")
SCRIPT1 = os.path.join(DASHBOARD_DIR, "Deshbord1.py")
SCRIPT2 = os.path.join(DASHBOARD_DIR, "Deshbord2.py")
SCRIPT3 = os.path.join(DASHBOARD_DIR, "odd", "Folder26195", "script3", "Link_Generator.py")
SCRIPT4 = os.path.join(DASHBOARD_DIR, "Deshbord4.py")

# === DARKEN FUNCTION ===
def darken(hex_color):
    import colorsys
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, max(0, l - 0.1), s)
    return '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))

# === SCRIPT LAUNCH FUNCTION ===
def open_dashboard_and_close(main_window, script_path):
    main_window.destroy()
    subprocess.Popen([sys.executable, script_path], shell=True)

# === BUTTON MAKER ===
def make_button(master, text, bg_color, command, corner_radius=30):
    btn = ctk.CTkButton(
        master,
        text=text,
        command=command,
        fg_color=bg_color,
        hover_color=darken(bg_color),
        text_color="#FFFFFF",
        font=("Segoe UI", 16, "bold"),
        corner_radius=corner_radius,
        height=50,
        width=300
    )
    def on_enter(e):
        btn.configure(width=310, height=54)
    def on_leave(e):
        btn.configure(width=300, height=50)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    btn.pack(pady=10)
    return btn

# === MAIN DASHBOARD ===
def show_dashboard():
    dash = ctk.CTk()
    dash.title("EasySell Dashboard")

    if os.path.exists(ICON_PATH):
        dash.iconbitmap(ICON_PATH)
    else:
        print("⚠️ Dashboard icon not found:", ICON_PATH)

    dash.geometry("950x850")
    dash.configure(fg_color="#F8F9FA")

    ctk.CTkLabel(dash, text="EasySell Dashboard", font=("Segoe UI", 28, "bold"), text_color="#1E2A38").pack(pady=(60, 10))
    ctk.CTkLabel(dash, text="📊", font=("Segoe UI", 40), text_color="#1E2A38").pack(pady=(0, 30))

    make_button(dash, "1. Find Detail", "#007BFF", lambda: open_dashboard_and_close(Deshbord1))
    make_button(dash, "2. Live Images", "#28A745", lambda: open_dashboard_and_close(Deshbord2))
    make_button(dash, "3. Get Direct Link Into Images", "#17A2B8", lambda: open_dashboard_and_close("Deshbord", "odd", "Folder26195", "script3", "Link_Generator.py"))
    make_button(dash, "4. Others", "#FFC107", lambda: open_dashboard_and_close(Deshbord3))

    make_button(dash, "❌ Close", "#DC3545", dash.destroy, corner_radius=8)

    dash.mainloop()

# === SESSION EXPIRY CONTROL ===
FLAG_FILE = "first_run.flag"
EXPIRE_HOURS = 3

def is_session_expired():
    if not os.path.exists(FLAG_FILE):
        return True
    try:
        with open(FLAG_FILE, "r") as f:
            timestamp = float(f.read().strip())
        expire_time = datetime.fromtimestamp(timestamp) + timedelta(hours=EXPIRE_HOURS)
        return datetime.now() > expire_time
    except:
        return True

def mark_unlocked():
    with open(FLAG_FILE, "w") as f:
        f.write(str(time.time()))

# === WELCOME SCREEN WITH PASSWORD ===
def show_welcome_screen():
    root = ctk.CTk()
    root.title("EasySell Welcome")

    if os.path.exists(ICON_PATH):
        root.iconbitmap(ICON_PATH)
    else:
        print("⚠️ Welcome icon not found:", ICON_PATH)

    root.geometry("950x850")
    root.configure(fg_color="white")

    frame = ctk.CTkFrame(root, fg_color="white")
    frame.pack(expand=True)

    try:
        image = tk.PhotoImage(file=WELCOME_IMAGE_PATH)
        label = ctk.CTkLabel(frame, image=image, text="")
        label.image = image
        label.pack(pady=10)
    except:
        print("⚠️ Welcome image not found:", WELCOME_IMAGE_PATH)
        ctk.CTkLabel(frame, text="EasySell Dashboard", font=("Segoe UI", 30, "bold"), text_color="#1E2A38").pack(pady=30)

    ctk.CTkLabel(frame, text="Welcome to EasySell Tool", font=("Segoe UI", 20), text_color="#1E2A38").pack(pady=10)

    if is_session_expired():
        password_var = tk.StringVar()
        password_entry = ctk.CTkEntry(frame, placeholder_text="Enter Password", show="*", textvariable=password_var, width=300, height=40)
        password_entry.pack(pady=10)

        error_label = ctk.CTkLabel(frame, text="", text_color="red", font=("Segoe UI", 12))
        error_label.pack()

        show_password = tk.BooleanVar(value=False)
        def toggle_password():
            password_entry.configure(show="" if show_password.get() else "*")

        ctk.CTkCheckBox(frame, text="Show Password", variable=show_password, command=toggle_password).pack(pady=5)

        def validate_password():
            if password_var.get() == "Essay//1122":
                mark_unlocked()
                root.destroy()
                show_dashboard()
            else:
                error_label.configure(text="❌ Incorrect password. Please try again.")

        password_entry.bind("<Return>", lambda event: validate_password())

        ctk.CTkButton(
            frame,
            text="🔐 Start",
            fg_color="#007BFF",
            hover_color="#0056b3",
            text_color="#FFFFFF",
            font=("Segoe UI", 16, "bold"),
            corner_radius=30,
            width=300,
            height=50,
            command=validate_password
        ).pack(pady=20)
    else:
        ctk.CTkButton(
            frame,
            text="🔐 Start",
            fg_color="#007BFF",
            hover_color="#0056b3",
            text_color="#FFFFFF",
            font=("Segoe UI", 16, "bold"),
            corner_radius=30,
            width=300,
            height=50,
            command=lambda: [root.destroy(), show_dashboard()]
        ).pack(pady=40)

    root.mainloop()

# === ENTRY POINT ===
if __name__ == "__main__":
    show_welcome_screen()
