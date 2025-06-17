#rohanshaj _K R
import tkinter as tk
import subprocess
import threading
import time
import os
import psutil
import json
import sys

# Fan mode mapping
fan_modes = {
    "Silent": 25,
    "Balanced": 50,
    "Performance": 75,
    "Turbo": 100,
    "Auto": -1
}

state_file = "/home/rohan/fan_state.txt"
current_mode = "Silent"
auto_mode_enabled = False
nbfc_popup = None

# ------------------ NBFC Fan Control ------------------
def set_fan_speed(speed):
    for fan in [0, 1]:
        try:
            result = subprocess.run(
                ["sudo", "/usr/bin/nbfc", "set", "--fan", str(fan), "--speed", str(speed)],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"[Info] Set fan {fan} to {speed}%: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            error = e.stderr.strip() if e.stderr else "Unknown error"
            print(f"[Error] NBFC fan {fan} (speed {speed}%): {error}")
        except Exception as e:
            print(f"[Error] NBFC fan {fan}: {e}")

def get_nbfc_status():
    try:
        result = subprocess.run(["sudo", "/usr/bin/nbfc", "status"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"[NBFC Error] {e.stderr.strip() if e.stderr else 'Unknown error'}"
    except Exception as e:
        return f"[NBFC Error] {e}"

# ------------------ Persistence ------------------
def save_fan_state(mode):
    try:
        with open(state_file, "w") as f:
            json.dump({"mode": mode}, f)
        os.chmod(state_file, 0o644)
    except Exception as e:
        print(f"[Error] Saving fan state: {e}")

def load_fan_state():
    try:
        if os.path.exists(state_file):
            with open(state_file, "r") as f:
                data = json.load(f)
                mode = data.get("mode", "Silent")
                if mode in fan_modes:
                    return mode
    except Exception as e:
        print(f"[Error] Loading fan state: {e}")
    return "Silent"

# ------------------ Auto Mode ------------------
def apply_mode(mode):
    global current_mode, auto_mode_enabled
    current_mode = mode
    save_fan_state(mode)
    if mode == "Auto":
        auto_mode_enabled = True
    else:
        auto_mode_enabled = False
        set_fan_speed(fan_modes[mode])
    update_mode_label()

def auto_mode_loop():
    while True:
        if auto_mode_enabled:
            temp = get_cpu_temp()
            if temp is None:
                temp = 0
            if temp < 45:
                set_fan_speed(fan_modes["Silent"])
            elif temp < 60:
                set_fan_speed(fan_modes["Balanced"])
            elif temp < 75:
                set_fan_speed(fan_modes["Performance"])
            else:
                set_fan_speed(fan_modes["Turbo"])
        time.sleep(5)

# ------------------ System Info ------------------
def get_cpu_temp():
    try:
        for hwmon in os.listdir("/sys/class/hwmon/"):
            name_path = f"/sys/class/hwmon/{hwmon}/name"
            if os.path.exists(name_path):
                with open(name_path) as f:
                    if "k10temp" in f.read().strip():
                        with open(f"/sys/class/hwmon/{hwmon}/temp1_input") as tf:
                            return int(tf.read()) / 1000
    except Exception as e:
        print(f"[Error] Getting CPU temp: {e}")
    return None

def get_nvidia_gpu_temp():
    try:
        output = subprocess.check_output(["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"], text=True)
        return int(output.strip().split('\n')[0])
    except Exception as e:
        print(f"[Error] Getting NVIDIA GPU temp: {e}")
        return None

def get_stats():
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        temp = get_cpu_temp()
        gpu_temp = get_nvidia_gpu_temp()
        return cpu, ram.percent, temp, gpu_temp
    except Exception as e:
        print(f"[Error] Getting stats: {e}")
        return 0, 0, None, None

# ------------------ UI ------------------
def update_mode_label():
    mode_label.config(text=f"Mode: {current_mode}")

def update_stats_label():
    cpu, ram, temp, gpu_temp = get_stats()
    temp_val = temp if temp is not None else 0
    gpu_val = f"{gpu_temp}°C" if gpu_temp is not None else "N/A"

    stats_text = f"CPU: {cpu:.1f}%\nRAM: {ram:.1f}%\nCPU Temp: {temp_val:.1f}°C\nNVIDIA GPU: {gpu_val}"
    stats_label.config(text=stats_text)

    if temp_val < 50:
        stats_label.config(fg="green")
    elif temp_val < 70:
        stats_label.config(fg="orange")
    else:
        stats_label.config(fg="red")

    root.after(3000, update_stats_label)

def on_mode_button(mode):
    apply_mode(mode)

def show_nbfc_popup():
    global nbfc_popup
    if nbfc_popup and tk.Toplevel.winfo_exists(nbfc_popup):
        nbfc_popup.lift()
        return

    nbfc_popup = tk.Toplevel(root)
    nbfc_popup.title("NBFC Status - Live")
    nbfc_popup.geometry("500x400")
    nbfc_popup.configure(bg="#1e1e1e")

    text_box = tk.Text(nbfc_popup, wrap="word", font=("Courier", 10), bg="#1e1e1e", fg="#cccccc")
    text_box.pack(fill="both", expand=True, padx=10, pady=10)

    def update_nbfc_output():
        if not tk.Toplevel.winfo_exists(nbfc_popup):
            return
        output = get_nbfc_status()
        text_box.config(state="normal")
        text_box.delete("1.0", tk.END)
        text_box.insert("1.0", output)
        text_box.config(state="disabled")
        nbfc_popup.after(3000, update_nbfc_output)

    update_nbfc_output()

# ------------------ Build GUI ------------------
root = tk.Tk()
root.title("Victus Fan Controller")
root.geometry("340x450")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

tk.Label(root, text="HP Victus Fan Control", font=("Helvetica", 16, "bold"), bg="#1e1e1e", fg="#00d4ff").pack(pady=10)

mode_label = tk.Label(root, text="Mode: Loading...", font=("Helvetica", 12), bg="#1e1e1e", fg="#ffffff")
mode_label.pack(pady=5)

stats_label = tk.Label(root, text="Stats Loading...", font=("Courier", 11), bg="#1e1e1e")
stats_label.pack(pady=5)

button_frame = tk.Frame(root, bg="#1e1e1e")
button_frame.pack(pady=10)

btn_style = {
    "font": ("Arial", 10),
    "width": 20,
    "bg": "#333333",
    "fg": "#ffffff",
    "activebackground": "#555555",
    "relief": "ridge",
    "bd": 2,
    "highlightthickness": 0
}

for mode in fan_modes:
    tk.Button(button_frame, text=mode, command=lambda m=mode: on_mode_button(m), **btn_style).pack(pady=3)

tk.Button(root, text="NBFC Info", command=show_nbfc_popup, bg="#00d4ff", fg="#000000", font=("Arial", 10, "bold")).pack(pady=5)
tk.Button(root, text="Quit", command=root.destroy, bg="#ff4444", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

# ------------------ Start ------------------
try:
    apply_mode(load_fan_state())
    threading.Thread(target=auto_mode_loop, daemon=True).start()
    update_stats_label()
    root.mainloop()
except Exception as e:
    print(f"[Error] Application failed: {e}")
    sys.exit(1)
