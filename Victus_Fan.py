import tkinter as tk
import subprocess
import threading
import time
import os
import psutil
import pystray
from PIL import Image, ImageDraw

fan_modes = {
    "Silent": 25,
    "Balanced": 50,
    "Performance": 75,
    "Turbo": 100,
    "Auto": -1
}

root = tk.Tk()
root.title("HP Victus Fan Controller")
root.geometry("350x550")
root.configure(bg="#1e1e2e")

current_mode = tk.StringVar()
current_mode.set("Silent")

def get_cpu_temp():
    try:
        with open("/sys/class/hwmon/hwmon4/temp1_input") as f:
            return int(f.read()) / 1000
    except:
        return None

def get_cpu_usage():
    return psutil.cpu_percent(interval=0.5)

def get_ram_usage():
    mem = psutil.virtual_memory()
    return mem.used / (1024 ** 3), mem.total / (1024 ** 3)

def get_gpu_info():
    info = {}

    try:
        output = subprocess.check_output([
            "nvidia-smi", "--query-gpu=name,utilization.gpu,temperature.gpu,memory.used,memory.total",
            "--format=csv,noheader,nounits"
        ]).decode().strip()
        name, usage, temp, mem_used, mem_total = output.split(", ")
        info["nvidia"] = {
            "name": name,
            "usage": int(usage),
            "temp": int(temp),
            "mem_used": int(mem_used),
            "mem_total": int(mem_total)
        }
    except:
        info["nvidia"] = None

    try:
        for hwmon in os.listdir("/sys/class/hwmon/"):
            name_path = f"/sys/class/hwmon/{hwmon}/name"
            if os.path.exists(name_path):
                with open(name_path) as f:
                    name = f.read().strip()
                    if "amdgpu" in name:
                        temp_path = f"/sys/class/hwmon/{hwmon}/temp1_input"
                        if os.path.exists(temp_path):
                            with open(temp_path) as tf:
                                temp = int(tf.read()) / 1000
                                info["amd"] = {
                                    "name": "AMD iGPU",
                                    "temp": round(temp, 1),
                                    "usage": None
                                }
                                break
    except:
        info["amd"] = None

    return info

def set_fan_speed(speed):
    try:
        subprocess.run(["sudo", "nbfc", "set", "--fan", "0", "--speed", str(speed)], check=True)
        subprocess.run(["sudo", "nbfc", "set", "--fan", "1", "--speed", str(speed)], check=True)
        subprocess.run(["sudo", "nbfc", "restart"], check=True)
        status_label.config(text=f"Manual Mode: Set fan speed to {speed}%")
    except subprocess.CalledProcessError:
        status_label.config(text="Failed to set fan speed")

def apply_mode(mode_name):
    global auto_mode_enabled
    current_mode.set(mode_name)
    if mode_name == "Auto":
        auto_mode_enabled = True
        status_label.config(text="Auto Mode Enabled")
    else:
        auto_mode_enabled = False
        speed = fan_modes[mode_name]
        set_fan_speed(speed)

def auto_mode_loop():
    while True:
        if current_mode.get() == "Auto":
            temp = get_cpu_temp()
            if temp is not None:
                if temp < 45:
                    set_fan_speed(fan_modes["Silent"])
                elif temp < 60:
                    set_fan_speed(fan_modes["Balanced"])
                elif temp < 75:
                    set_fan_speed(fan_modes["Performance"])
                else:
                    set_fan_speed(fan_modes["Turbo"])
                status_label.config(text=f"Auto Mode: CPU Temp {temp:.1f}°C")
        time.sleep(10)

def update_stats():
    while True:
        cpu_temp = get_cpu_temp()
        cpu_usage = get_cpu_usage()
        gpu_info = get_gpu_info()
        ram_used, ram_total = get_ram_usage()

        cpu_temp_label.config(text=f"CPU Temp: {cpu_temp:.1f}°C" if cpu_temp else "CPU Temp: N/A")
        cpu_usage_label.config(text=f"CPU Usage: {cpu_usage:.1f}%")
        ram_label.config(text=f"RAM: {ram_used:.1f} / {ram_total:.1f} GB")

        if gpu_info.get("nvidia"):
            n = gpu_info["nvidia"]
            gpu_n_label.config(text=f"NVIDIA {n['name']}: {n['usage']}% @ {n['temp']}°C ({n['mem_used']}/{n['mem_total']}MB)")
        else:
            gpu_n_label.config(text="NVIDIA: N/A")

        if gpu_info.get("amd"):
            a = gpu_info["amd"]
            gpu_a_label.config(text=f"{a['name']}: {a['temp']}°C")
        else:
            gpu_a_label.config(text="AMD: N/A")

        time.sleep(5)

def start_nbfc():
    subprocess.run(["sudo", "nbfc", "start"])

# Create a simple tray icon image (purple circle)
def create_image():
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((8, 8, 56, 56), fill="#bd93f9")
    return image

# Show the window again from tray
def show_window(icon, item):
    icon.stop()
    root.after(0, root.deiconify)

# Exit the program cleanly
def exit_app(icon, item):
    icon.stop()
    root.after(0, root.destroy)

# Hide the window and show tray icon
def on_closing():
    root.withdraw()
    image = create_image()
    menu = pystray.Menu(
        pystray.MenuItem('Show', show_window),
        pystray.MenuItem('Exit', exit_app)
    )
    icon = pystray.Icon("HP Victus Fan Controller", image, "Fan Controller", menu)
    threading.Thread(target=icon.run, daemon=True).start()
    status_label.config(text="Window hidden. Tray icon running.")

root.protocol("WM_DELETE_WINDOW", on_closing)

# ------------------ UI ------------------

tk.Label(root, text="Fan Modes", font=("Helvetica", 16), bg="#1e1e2e", fg="#f8f8f2").pack(pady=10)

mode_frame = tk.Frame(root, bg="#1e1e2e")
mode_frame.pack()

for mode in fan_modes:
    tk.Radiobutton(
        mode_frame,
        text=mode,
        variable=current_mode,
        value=mode,
        indicatoron=False,
        width=20,
        height=2,
        command=lambda m=mode: apply_mode(m),
        bg="#44475a",
        fg="#f8f8f2",
        activebackground="#6272a4",
        selectcolor="#bd93f9"
    ).pack(pady=4)

tk.Label(root, text="System Stats", font=("Helvetica", 14), bg="#1e1e2e", fg="#ffb86c").pack(pady=10)

cpu_temp_label = tk.Label(root, text="CPU Temp: ...", bg="#1e1e2e", fg="#50fa7b", font=("Helvetica", 12))
cpu_temp_label.pack()

cpu_usage_label = tk.Label(root, text="CPU Usage: ...", bg="#1e1e2e", fg="#8be9fd", font=("Helvetica", 12))
cpu_usage_label.pack()

gpu_n_label = tk.Label(root, text="NVIDIA: ...", bg="#1e1e2e", fg="#8be9fd", font=("Helvetica", 12))
gpu_n_label.pack()

gpu_a_label = tk.Label(root, text="AMD: ...", bg="#1e1e2e", fg="#ffb86c", font=("Helvetica", 12))
gpu_a_label.pack()

ram_label = tk.Label(root, text="RAM: ...", bg="#1e1e2e", fg="#f1fa8c", font=("Helvetica", 12))
ram_label.pack()

status_label = tk.Label(root, text="NBFC Service Starting...", bg="#1e1e2e", fg="#f8f8f2", font=("Helvetica", 10))
status_label.pack(pady=10)

auto_mode_enabled = False

start_nbfc()
threading.Thread(target=update_stats, daemon=True).start()
threading.Thread(target=auto_mode_loop, daemon=True).start()

root.mainloop()
