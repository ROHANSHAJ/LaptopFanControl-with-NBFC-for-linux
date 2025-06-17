
# 🌀 NBFC Fan Controller GUI for Linux

A Python-based GUI app to control your laptop’s fans using [NBFC (NoteBook FanControl)](https://github.com/hirschmann/nbfc) on Linux.  
Includes **manual fan control**, **auto mode based on CPU temperature**, **system monitoring**, and **tray icon support**.

---

## ✅ Compatibility

**Tested On:**
- **Laptop:** HP Victus 15 (by author)
- **OS:** Linux Mint 22.1 x86_64

---

## 🚀 Features

- 🧊 **Fan Control Modes**:
  - Silent (25%)
  - Balanced (50%)
  - Performance (75%)
  - Turbo (100%)
  - Auto (dynamic based on CPU temp)

- 📈 **System Monitoring**:
  - CPU temperature and usage
  - GPU temperature (NVIDIA/AMD)
  - RAM usage

- 🧲 **System Tray Support**:
  - Minimize to tray (purple dot icon)
  - Restore GUI or exit app via tray

- ⚙️ **NBFC Auto Setup**:
  - Installs and builds NBFC
  - Prompts user to select profile

- 💻 **User-Friendly GUI**:
  - Dark-themed Tkinter interface
  - Status bar with real-time info

---

## 🛠️ Setup Options

### 🔹 Option 1: Automatic Setup (Recommended)

1. **Run the app with sudo**:
   ```bash
   sudo python3 nbfc_fan_controller.py
   ```

2. On first run:
   - Installs NBFC if not found
   - Builds and configures it
   - Prompts to select compatible NBFC profile

> ✅ This is the easiest and fastest way to get started.

---

### 🔸 Option 2: Manual Setup

#### 1. Install System Dependencies:

```bash
sudo apt update
sudo apt install -y python3 python3-pip git build-essential mono-complete lm-sensors
```

#### 2. Install Python Dependencies:

```bash
pip3 install psutil pystray pillow
```

#### 3. Clone and Build NBFC:

```bash
git clone https://github.com/nbfc-linux/nbfc-linux.git /tmp/nbfc-linux
cd /tmp/nbfc-linux
make
sudo make install
```

> *(Optional)* Install config probe tool:  
> `sudo apt install nbfc-linux-probe`

#### 4. Configure NBFC:

```bash
nbfc config -l                     # List available configs
sudo nbfc config -s "Your Laptop" # Replace with your model
sudo systemctl restart nbfc_service
sudo nbfc start
```

#### 5. Run the App:

```bash
sudo python3 nbfc_fan_controller.py
```

> Run `Victus_fans.py` only **after** `all_fans.py` if you use both scripts.

---

## 📖 Usage Guide

- **Fan Control**: Select a fan mode or use **Auto** (dynamic adjustment).
- **Minimize**: Close window to tray.
- **Tray Menu**: Right-click tray icon to restore or exit.

#### 🔄 Auto Fan Logic:

| CPU Temp      | Mode        |
|---------------|-------------|
| < 45°C        | Silent      |
| 45–59°C       | Balanced    |
| 60–74°C       | Performance |
| ≥ 75°C        | Turbo       |

---

## 🧪 Troubleshooting

- **Fan not responding**:
  - Check NBFC status: `journalctl -u nbfc_service`
  - Ensure proper config selected: `nbfc config -l`

- **No temperature shown**:
  - Run: `sensors`
  - Verify `coretemp` or `amdgpu` is in `/sys/class/hwmon/`

- **No sudo**: App runs in monitoring-only mode without root.

---

## 🔁 Run on Startup (Optional)

1. Create systemd service:

```bash
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/nbfc-fan-controller.service
```

2. Paste:

```ini
[Unit]
Description=NBFC Fan Controller GUI
After=graphical-session.target

[Service]
ExecStart=/usr/bin/sudo /usr/bin/python3 /path/to/nbfc_fan_controller.py
Restart=always

[Install]
WantedBy=graphical-session.target
```

3. Enable the service:

```bash
systemctl --user enable nbfc-fan-controller.service
systemctl --user start nbfc-fan-controller.service
```

---

## 🧾 License

MIT License – use freely, attribution appreciated.

---

## 🙌 Acknowledgments

- [NBFC-Linux](https://github.com/nbfc-linux/nbfc-linux)
- [`psutil`](https://pypi.org/project/psutil/)
- [`pystray`](https://pypi.org/project/pystray/)
- [`Pillow`](https://pypi.org/project/Pillow/)
- Linux open-source community

---

📬 *Found bugs? Have ideas? Open an issue or contribute!*
