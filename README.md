## ✅ Compatibility
**Tested on:** HP Victus 15 (by me) 


# Fan Controller GUI for Linux (NBFC-based) for all laptops

A Python GUI application to control your laptop fans on Linux using [NBFC (NoteBook FanControl)](https://github.com/hirschmann/nbfc) backend.  
The app supports manual fan speed modes as well as an automatic mode based on CPU temperature, and displays system stats like CPU/GPU temperature, usage, and RAM usage.

---

## Features

- Manual fan speed control modes: **Silent, Balanced, Performance, Turbo**
- Automatic fan speed adjustment based on CPU temperature
- Display real-time system stats:
  - CPU temperature and usage
  - GPU info (NVIDIA and AMD supported)
  - RAM usage
- Tray icon support with show/hide and exit options
- Automatic setup and installation of NBFC and its dependencies (requires sudo)
- User-friendly Tkinter GUI with modern dark theme

---

## Requirements

- Python 3.x
- Linux system with NBFC support (tested on Ubuntu/Debian)
- Dependencies (install via pip and apt):
  - `tkinter` (usually preinstalled with Python)
  - `psutil` (`pip install psutil`)
  - `pystray` (`pip install pystray`)
  - `Pillow` (`pip install pillow`)
  - `mono-complete`, `git`, `build-essential` (installed automatically if run with sudo)

---

## Installation & Setup

1. Clone or download this repository.

2. Ensure Python 3 and required packages are installed:

   ```bash
   sudo apt update
   sudo apt install python3 python3-pip git build-essential mono-complete
   pip3 install psutil pystray pillow
   ```

3. Run the script (preferably with sudo for full fan control functionality):

   ```bash
   sudo python3 nbfc_fan_controller.py
   ```

4. On first run, the app will attempt to install and build NBFC automatically and prompt you to select a suitable NBFC configuration for your laptop model.

---

## Usage

- Select a fan mode to manually set fan speed or choose **Auto** to let the app adjust fan speeds based on CPU temperature.
- System stats update every few seconds.
- Close the window to minimize the app to the system tray. Use the tray icon menu to show the window or exit.

---

## Notes

- Running without sudo will show a warning and may limit fan control capabilities.
- NBFC configurations must match your laptop model for fan control to work properly.
- Tested on HP Victus 15 with AMD APU and Nvidia GPU under Linux.

- only run Victus_fans.py after runnuing all_fans,py

---

## Troubleshooting

- If fan speeds do not change, check that NBFC service is running and your config is applied.
- Run the app with sudo to ensure permissions.
- Verify NBFC installation manually via terminal commands:
  ```bash
  nbfc --version
  nbfc config -l
  ```

---

## License

This project is open source under the MIT License.

---

## Acknowledgments

- [NBFC-Linux](https://github.com/nbfc-linux/nbfc-linux) for fan control backend
- `psutil`, `pystray`, `Pillow` libraries for system monitoring and tray icon functionality
- Tkinter for GUI framework

---

Feel free to open issues or contribute!
