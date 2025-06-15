import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import os
import psutil
import pystray
from PIL import Image, ImageDraw
import sys
import uuid
import getpass

# Fan modes with corresponding speed percentages
fan_modes = {
    "Silent": 25,
    "Balanced": 50,
    "Performance": 75,
    "Turbo": 100,
    "Auto": -1
}

def check_sudo():
    """Check if the script is running with sudo privileges."""
    if os.geteuid() != 0:
        messagebox.showwarning("Permission Warning", "This script requires sudo privileges for full functionality. Run with: sudo python3 nbfc_fan_controller.py\nContinuing without sudo...")
        return False
    return True

def run_command(command, check=False, shell=True):
    """Run a shell command and return its output, ignoring errors if check=False."""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"

def setup_nbfc(status_label_setup):
    """Automate NBFC installation and setup, continuing on failure."""
    commands = [
        ("apt update", "Updating package lists"),
        ("apt install -y git build-essential mono-complete", "Installing dependencies"),
        ("git clone https://github.com/nbfc-linux/nbfc-linux.git /tmp/nbfc-linux || true", "Cloning NBFC repository"),
        ("cd /tmp/nbfc-linux && make && make install", "Building and installing NBFC"),
        ("apt install -y nbfc-linux-probe", "Installing nbfc-linux-probe")
    ]
    
    for cmd, desc in commands:
        status_label_setup.config(text=f"{desc}...")
        print(f"Executing: {cmd}")
        output = run_command(cmd, check=False)
        if "Error" in output:
            status_label_setup.config(text=f"Warning: {desc} failed: {output}")
            time.sleep(2)  # Brief pause to show warning
        else:
            status_label_setup.config(text=f"{desc} completed.")
            time.sleep(1)
    
    # Check if NBFC is installed
    output = run_command("nbfc --version", check=False)
    if "Error" not in output:
        return True
    status_label_setup.config(text="Warning: NBFC not installed, fan control may not work.")
    return False

def get_nbfc_configs():
    """Retrieve the list of available NBFC configurations."""
    output = run_command("nbfc config -l", check=False)
    if "Error" in output:
        messagebox.showwarning("Warning", f"Failed to retrieve NBFC configs: {output}\nContinuing with GUI...")
        return []
    return output.splitlines()

def apply_nbfc_config(config_name):
    """Apply the selected NBFC configuration."""
    output = run_command(f"nbfc config -s \"{config_name}\"", check=False)
    if "Error" in output:
        messagebox.showwarning("Warning", f"Failed to apply config {config_name}: {output}\nContinuing with GUI...")
        return False
    run_command("systemctl restart nbfc_service", check=False)
    return True

def get_cpu_temp():
    """Get CPU temperature from hwmon."""
    try:
        for hwmon in os.listdir("/sys/class/hwmon/"):
            name_path = f"/sys/class/hwmon/{hwmon}/name"
            if os.path.exists(name_path):
                with open(name_path) as f:
                    if "coretemp" in f.read().strip():
                        temp_path = f"/sys/class/hwmon/{hwmon}/temp1_input"
                        if os.path.exists(temp_path):
                            with open(temp_path) as tf:
                                return int(tf.read()) / 1000
        return None
    except:
        return None

def get_cpu_usage():
    """Get CPU usage percentage."""
    return psutil.cpu_percent(interval=0.5)

def get_ram_usage():
    """Get RAM usage in GB."""
    mem = psutil.virtual_memory()
    return mem.used / (1024 ** 3), mem.total / (1024 ** 3)

def get_gpu_info():
    """Get GPU information (NVIDIA and AMD)."""
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
    """Set fan speed for both fans."""
    try:
        subprocess.run(["nbfc", "set", "--fan", "0", "--speed", str(speed)], check=True)
        subprocess.run(["nbfc", "set", "--fan", "1", "--speed", str(speed)], check=True)
        subprocess.run(["nbfc", "restart"], check=True)
        status_label.config(text=f"Manual Mode: Set fan speed to {speed}%")
    except subprocess.CalledProcessError:
        status_label.config(text="Failed to set fan speed. NBFC may not be configured.")

def apply_mode(mode_name):
    """Apply the selected fan mode."""
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
    """Automatically adjust fan speed based on CPU temperature."""
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
    """Update system stats in the GUI."""
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
    """Start the NBFC service."""
    output = run_command("nbfc start", check=False)
    if "Error" in output:
        status_label.config(text="Failed to start NBFC service.")

def create_image():
    """Create a system tray icon image (purple circle)."""
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((8, 8, 56, 56), fill="#bd93f9")
    return image

def show_window(icon, item):
    """Show the main window from the system tray."""
    icon.stop()
    root.after(0, root.deiconify)

def exit_app(icon, item):
    """Exit the application cleanly."""
    icon.stop()
    root.after(0, root.destroy)

def on_closing():
    """Hide the window and show the system tray icon."""
    root.withdraw()
    image = create_image()
    menu = pystray.Menu(
        pystray.MenuItem('Show', show_window),
        pystray.MenuItem('Exit', exit_app)
    )
    icon = pystray.Icon("Fan Controller", image, "Fan Controller", menu)
    threading.Thread(target=icon.run, daemon=True).start()
    status_label.config(text="Window hidden. Tray icon running.")

def setup_and_select_config():
    """Setup NBFC and prompt user to select a configuration."""
    setup_window = tk.Toplevel(root)
    setup_window.title("NBFC Setup")
    setup_window.geometry("400x300")
    setup_window.configure(bg="#1e1e2e")

    tk.Label(setup_window, text="Setting up NBFC...", font=("Helvetica", 14), bg="#1e1e2e", fg="#f8f8f2").pack(pady=10)
    status_label_setup = tk.Label(setup_window, text="Checking privileges...", bg="#1e1e2e", fg="#f8f8f2")
    status_label_setup.pack(pady=10)

    def perform_setup():
        # Check sudo and proceed even if not present
        has_sudo = check_sudo()
        if not has_sudo:
            status_label_setup.config(text="Running without sudo. Some features may be limited.")
            time.sleep(2)

        # Attempt NBFC setup
        nbfc_installed = setup_nbfc(status_label_setup)

        # Proceed to configuration selection
        status_label_setup.config(text="NBFC setup complete. Select a configuration:")
        configs = get_nbfc_configs()
        if not configs:
            status_label_setup.config(text="No configurations found. Starting GUI...")
            time.sleep(2)
            setup_window.destroy()
            start_nbfc()
            threading.Thread(target=update_stats, daemon=True).start()
            threading.Thread(target=auto_mode_loop, daemon=True).start()
            return

        config_var = tk.StringVar()
        config_combobox = ttk.Combobox(setup_window, textvariable=config_var, values=configs, state="readonly", width=50)
        config_combobox.pack(pady=10)
        config_combobox.set(configs[0])

        def apply_and_close():
            selected_config = config_var.get()
            if apply_nbfc_config(selected_config):
                status_label_setup.config(text=f"Applied config: {selected_config}")
            else:
                status_label_setup.config(text=f"Failed to apply config: {selected_config}. Starting GUI...")
            time.sleep(2)
            setup_window.destroy()
            start_nbfc()
            threading.Thread(target=update_stats, daemon=True).start()
            threading.Thread(target=auto_mode_loop, daemon=True).start()

        tk.Button(setup_window, text="Apply Config", command=apply_and_close, bg="#bd93f9", fg="#f8f8f2").pack(pady=10)

    threading.Thread(target=perform_setup, daemon=True).start()

# Main application window
root = tk.Tk()
root.title("Fan Controller")
root.geometry("350x550")
root.configure(bg="#1e1e2e")
root.protocol("WM_DELETE_WINDOW", on_closing)

# UI Elements
tk.Label(root, text="Fan Modes", font=("Helvetica", 16), bg="#1e1e2e", fg="#f8f8f2").pack(pady=10)

mode_frame = tk.Frame(root, bg="#1e1e2e")
mode_frame.pack()

current_mode = tk.StringVar()
current_mode.set("Silent")

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

status_label = tk.Label(root, text="Initializing...", bg="#1e1e2e", fg="#f8f8f2", font=("Helvetica", 10))
status_label.pack(pady=10)

auto_mode_enabled = False

# Start NBFC setup and configuration selection
setup_and_select_config()

root.mainloop() #rohanshaj_KRs