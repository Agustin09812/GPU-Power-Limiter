import os
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from xml.etree import ElementTree as ET
import shutil
import sys
from subprocess import STARTUPINFO, STARTF_USESHOWWINDOW, SW_HIDE

# CMD WINDOWS
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE

NO_WINDOW = {
    "startupinfo": startupinfo,
    "creationflags": subprocess.CREATE_NO_WINDOW
}

# ==========================================================
# MAIN ROUTES
# ==========================================================
APP_DIR = r"C:\GPU Power Limit"
SERVICE_ID = "dGPU_Power_Limiter"  # SERVICE NAME
SERVICE_EXE = os.path.join(APP_DIR, "dGPU_Power_Limiter.exe")
XML_PATH = os.path.join(APP_DIR, "dGPU_Power_Limiter.xml")
LOG_DIR = os.path.join(APP_DIR, "logs")

def open_install_folder():
    try:
        if os.path.exists(APP_DIR):
            subprocess.Popen(f'explorer "{APP_DIR}"')
        else:
            messagebox.showwarning("Folder not found", "The service folder does not exist yet.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# ==========================================================
# UTILITIES
# ==========================================================
def resource_path(relative):
    return os.path.join(getattr(sys, "_MEIPASS", os.path.abspath(".")), relative)

def center_window(win, w, h):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw // 2) - (w // 2)
    y = (sh // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

def get_default_tdp():
    try:
        out = subprocess.check_output(["nvidia-smi", "-q", "-d", "POWER"], text=True, **NO_WINDOW)
        for line in out.split("\n"):
            if "Default Power Limit" in line:
                return int(line.split(":")[1].replace("W", "").strip())
    except:
        return 95
    return 95

def get_current_tdp():
    try:
        out = subprocess.check_output(["nvidia-smi", "-q", "-d", "POWER"], text=True, **NO_WINDOW)
        for line in out.split("\n"):
            if "Power Limit" in line and "Default" not in line:
                return line.split(":")[1].strip()
    except:
        return "Unknow"
    return "Unknow"

def read_status():
    try:
        def get_gpu_info():
            try:
                return subprocess.check_output(
                    ["nvidia-smi", "-q", "-d", "POWER"],
                    text=True,
                    **NO_WINDOW
                )
            except Exception as e:
                return f"Error:\n{str(e)}"

        # LOAD INITIAL INFO
        output = get_gpu_info()

        # CREATE WINDOW
        top = tk.Toplevel(root)
        top.title("GPU status")
        top.geometry("650x650")
        top.configure(bg="#1a1a1a")

        center_window(top, 650, 650)

        # FRAME FOR TEXT + SCROLL
        text_frame = ttk.Frame(top)
        text_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # TEXT BOX
        text = tk.Text(
            text_frame,
            bg="#1a1a1a",
            fg="white",
            font=("Consolas", 11),
            wrap="none",
            border=0
        )
        text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text.yview)
        scrollbar.pack(side="right", fill="y")
        text.configure(yscrollcommand=scrollbar.set)

        def format_output(raw):
            lines = raw.strip().split("\n")
            formatted = ""
            for line in lines:
                if ":" in line:
                    left, right = line.split(":", 1)
                    formatted += f"{left:<30}: {right.strip()}\n"
                else:
                    formatted += line + "\n"
            return formatted

        text.insert("1.0", format_output(output))
        text.config(state="disabled")

        # ======================
        # BUTTONS SIDE BY SIDE
        # ======================
        btn_frame = ttk.Frame(top)
        btn_frame.pack(pady=15)

        def refresh():
            new_output = get_gpu_info()
            formatted = format_output(new_output)

            text.config(state="normal")
            text.delete("1.0", "end")
            text.insert("1.0", formatted)
            text.config(state="disabled")

        refresh_btn = ttk.Button(btn_frame, text="Refresh Info", command=refresh)
        refresh_btn.grid(row=0, column=0, padx=10)

        close_btn = ttk.Button(btn_frame, text="Close", command=top.destroy)
        close_btn.grid(row=0, column=1, padx=10)

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ==========================================================
# SERVICE: WinSW
# ==========================================================
def extract_winsw():
    src = resource_path("winsw.exe")
    if not os.path.exists(src):
        raise FileNotFoundError("winsw.exe not found.")

    shutil.copy(src, SERVICE_EXE)

def create_xml(tdp_value):
    xml = f"""<service>
  <id>{SERVICE_ID}</id>
  <name>GPU Power Limit Service</name>
  <description>NVIDIA GPU Power Limit Control</description>

  <executable>C:\\Windows\\System32\\cmd.exe</executable>
  <arguments>/c "nvidia-smi -pl {tdp_value}"</arguments>

  <logpath>{LOG_DIR}</logpath>
  <log mode="rotate"/>
</service>
"""
    with open(XML_PATH, "w", encoding="utf-8") as f:
        f.write(xml)


def get_service_state():
    if not os.path.exists(SERVICE_EXE):
        return "NOT_INSTALLED"

    if not os.path.exists(XML_PATH):
        return "NOT_INSTALLED"

    result = subprocess.run(["sc", "query", "dGPU_Power_Limiter"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **NO_WINDOW )

    txt = (result.stdout + result.stderr).lower()

    if "1060" in txt or "does not exist" in txt:
        return "NOT_INSTALLED"

    if "running" in txt:
        return "ACTIVE"

    if "stopped" in txt:
        if not os.path.exists(SERVICE_EXE) or not os.path.exists(XML_PATH):
            return "NOT_INSTALLED"
        return "INSTALLED"

    return "NOT_INSTALLED"

# ==========================================================
# FORCE UNINSTALL
# ==========================================================
def force_delete_service():
    subprocess.run(
        ["sc", "delete", "dGPU_Power_Limiter"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        **NO_WINDOW
    )

# ==========================================================
# INSTALL / UNINSTALL
# ==========================================================
def install_service():
    try:
        # 0) DELETE RECORDS
        force_delete_service()

        # 1) CREATE FOLDER
        os.makedirs(APP_DIR, exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)

        # 2) WinSW COPY
        extract_winsw()

        # 3) CREATE XML WITH CURRENT TDP
        create_xml(get_default_tdp())

        # 4) INSTALL SERVICE
        subprocess.run([SERVICE_EXE, "install"], check=True, **NO_WINDOW)

        # 5) INITIALIZE SERVICE
        subprocess.run([SERVICE_EXE, "start"], check=False, **NO_WINDOW)

        messagebox.showinfo("OK", "Service installed successfully.")
        update_ui()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def uninstall_service():
    try:
        subprocess.run([SERVICE_EXE, "stop"], check=False, **NO_WINDOW)
        subprocess.run([SERVICE_EXE, "uninstall"], check=False, **NO_WINDOW)

        shutil.rmtree(APP_DIR, ignore_errors=True)

        messagebox.showinfo("OK", "Service uninstalled.")
        update_ui()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ==========================================================
# ABOUT SECTION
# ==========================================================
def show_about():
    top = tk.Toplevel(root)
    top.title("About")
    top.configure(bg="#1a1a1a")
    top.geometry("500x400")
    center_window(top, 500, 400)

    # FIRST FRAME
    frame = ttk.Frame(top)
    frame.pack(fill="both", expand=True, padx=15, pady=15)

    # TEXT BOX
    text_frame = ttk.Frame(frame)
    text_frame.pack(fill="both", expand=True)

    txt = tk.Text(
        text_frame,
        bg="#1a1a1a",
        fg="white",
        font=("Segoe UI", 11),
        wrap="word",
        border=0
    )
    txt.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=txt.yview)
    scrollbar.pack(side="right", fill="y")
    txt.configure(yscrollcommand=scrollbar.set)

    info = (
        "GPU Power Limiter\n"
        "Versión 1.0\n\n"
        "This software allows you to manage the power limit of NVIDIA GPUs "
        "by running a background service with WinSW.\n\n"
        "Technologies used:\n"
        "• Python 3.11\n"
        "• Tkinter UI (Dark Mode)\n"
        "• WinSW (Windows Service Wrapper)\n"
        "• NVIDIA-SMI\n"
        "• PyInstaller"
    )

    txt.insert("1.0", info)
    txt.config(state="disabled")

    ttk.Button(top, text="Close", command=top.destroy).pack(pady=10)


# ==========================================================
# APPLY TDP
# ==========================================================
def apply_tdp(value):
    try:
        tree = ET.parse(XML_PATH)
        root = tree.getroot()

        for el in root.iter("arguments"):
            el.text = f'/c "nvidia-smi -pl {value}"'

        tree.write(XML_PATH)

        subprocess.run([SERVICE_EXE, "stop"], check=False, **NO_WINDOW)
        subprocess.run([SERVICE_EXE, "start"], check=False, **NO_WINDOW)

        messagebox.showinfo("OK", f"TDP changed to: {value}W")
        update_ui()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ==========================================================
# GUI DARK MODE
# ==========================================================
root = tk.Tk()
root.title("GPU Power Limiter")
root.iconbitmap(resource_path("logo.ico"))
root.minsize(800, 600)
center_window(root, 800, 600)

root.configure(bg="#1a1a1a")

style = ttk.Style()
style.theme_use("clam")
style.configure(".", background="#1a1a1a", foreground="white")
style.configure("TLabel", background="#1a1a1a", foreground="white")
style.configure("TButton", padding=6, font=("Segoe UI", 11))

frame = ttk.Frame(root)
frame.pack(expand=True)

# ----------------------------------------------------------
# UI ELEMENTS
# ----------------------------------------------------------

title = ttk.Label(frame, text="NVIDIA GPU Power Limit Control", font=("Segoe UI", 20))
title.pack(pady=(10, 5))

# SERVICE STATUS
service_label = ttk.Label(frame, text="Service: Checking...", font=("Segoe UI", 14, "bold"))
service_label.pack(pady=(5, 0))

# CURRENT TDP
current_tdp_label = ttk.Label(frame, text="Current TDP: ...", font=("Segoe UI", 12))
current_tdp_label.pack(pady=(0, 20))


# =============================
# TDP SELECTOR
# =============================
try:
    current_val = get_current_tdp().replace(" W", "").strip()
    if current_val.isdigit():
        tdp_var = tk.StringVar(value=current_val)
    else:
        tdp_var = tk.StringVar(value=str(get_default_tdp()))
except:
    tdp_var = tk.StringVar(value=str(get_default_tdp()))

selector = ttk.Combobox(
    frame,
    textvariable=tdp_var,
    values=["25", "30", "35", "40", "45", "50", "55", "60", "65", "70", "75", "80", "85", "90", "95", "100"],
    state="readonly"
)
selector.configure(foreground="black")
selector.pack(pady=5)

selector.bind("<Key>", lambda e: "break")

BTN_WIDTH = 16          # x
BTN_BIG_WIDTH = 22      # y (install/uninstall)


# =============================
# 1° Row → APPLY / APPLY DEFAULT
# =============================
row1 = ttk.Frame(frame)
row1.pack(pady=10)

apply_btn = ttk.Button(row1, text="Apply",
                       width=BTN_WIDTH,
                       command=lambda: apply_tdp(tdp_var.get()))
apply_btn.grid(row=0, column=0, padx=12)

default_btn = ttk.Button(row1, text="Apply Default",
                         width=BTN_WIDTH,
                         command=lambda: apply_tdp(get_default_tdp()))
default_btn.grid(row=0, column=1, padx=12)


# =============================
# 2° Row → VIEW STATUS / ABOUT
# =============================
row2 = ttk.Frame(frame)
row2.pack(pady=10)

status_btn = ttk.Button(row2, text="View Status",
                         width=BTN_WIDTH,
                         command=read_status)
status_btn.grid(row=0, column=0, padx=12)

about_btn = ttk.Button(row2, text="About",
                       width=BTN_WIDTH,
                       command=show_about)
about_btn.grid(row=0, column=1, padx=12)

folder_btn = ttk.Button(frame, text="Open Location",
                        width=BTN_BIG_WIDTH,
                        command=open_install_folder)
folder_btn.pack(pady=10)


# =============================
# INSTALL / UNINSTALL BUTTON
# =============================
toggle_btn = ttk.Button(frame, text="...", width=BTN_BIG_WIDTH)
toggle_btn.pack(pady=25)

# ==========================================================
# UI UPDATE
# ==========================================================
def update_ui():
    state = get_service_state()
    current = get_current_tdp()

    # SHOW CURRENT TDP
    current_tdp_label.config(text=f"Current TDP: {current}")

    # SERVICE: NOT INSTALLED
    if state == "NOT_INSTALLED":
        service_label.config(text="Service: NOT ACTIVE", foreground="red")
        toggle_btn.config(text="Install Service", command=install_service)

        apply_btn.config(state="disabled")
        default_btn.config(state="disabled")
        selector.config(state="disabled")

    # SERVICE: INSTALLED
    elif state == "INSTALLED":
        service_label.config(text="Service: INSTALLED", foreground="green")
        toggle_btn.config(text="Uninstall Service", command=uninstall_service)

        selector.config(state="readonly")
        default_btn.config(state="normal")
        apply_btn.config(state="normal")

    # SERVICE: ACTIVE
    elif state == "ACTIVE":
        service_label.config(text="Service: ACTIVE", foreground="green")
        toggle_btn.config(text="Uninstall Service", command=uninstall_service)

        selector.config(state="readonly")
        apply_btn.config(state="normal")
        default_btn.config(state="normal")

update_ui()
root.mainloop()