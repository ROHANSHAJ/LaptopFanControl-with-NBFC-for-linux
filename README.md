LaptopFanControl
A simple Python GUI application for controlling laptop fans on Ubuntu/Debian systems using NBFC-Linux. It automates the setup of NBFC, lets you choose from available fan configurations, and provides an easy-to-use interface to adjust fan speeds and monitor system stats like CPU, GPU, and RAM usage. The app includes a system tray icon for quick access and keeps running even if setup steps fail.
Features

Easy NBFC Setup: Automatically installs NBFC-Linux and required tools (git, build-essential, mono-complete, nbfc-linux-probe).
Fan Configuration: Choose from a list of NBFC fan profiles (via nbfc config -l) in a dropdown menu.
Fan Modes:
Silent (25% speed)
Balanced (50% speed)
Performance (75% speed)
Turbo (100% speed)
Auto (adjusts speed based on CPU temperature: <45°C, 45–60°C, 60–75°C, >75°C)


System Monitoring: Shows real-time CPU temperature, CPU usage, RAM usage, and NVIDIA/AMD GPU stats (if available).
System Tray Icon: Minimize to a system tray icon (purple circle) to restore or exit the app.
Keeps Going: Continues to the GUI with system monitoring even if NBFC setup or configuration fails, showing warnings for any issues.

Prerequisites

Operating System: Ubuntu/Debian (uses apt package manager). For other Linux distributions, edit the setup_nbfc function in the script.
Python 3: Requires Python 3.6 or higher.
Sudo Privileges: Needed for installing NBFC and controlling fans (optional for just monitoring system stats).
Internet Connection: Required to download dependencies and the NBFC-Linux repository.

Installation

Clone the Repository:
git clone https://github.com/your-username/LaptopFanControl.git
cd LaptopFanControl

Replace your-username with your GitHub username or the correct repository URL.

Install Python Dependencies:
pip install psutil pystray pillow

Install tkinter if it’s not already installed:
sudo apt install python3-tk


Run the Script:For full functionality (fan control and NBFC setup):
sudo python3 laptop_fan_control.py

For system monitoring only (without fan control):
python3 laptop_fan_control.py



Usage

First-Time Setup:

The script checks for sudo privileges and warns if they’re missing, but continues running.
It tries to install NBFC-Linux and its dependencies, showing progress and any warnings in a setup window.
A dropdown menu lists available NBFC fan configurations. Select one and click "Apply Config."
If setup or configuration fails, the app moves to the main GUI with a warning message.


Main GUI:

Fan Modes: Pick Silent, Balanced, Performance, Turbo, or Auto using radio buttons.
System Stats: View live updates for CPU temperature, CPU usage, RAM usage, and NVIDIA/AMD GPU stats (if available).
Auto Mode: Automatically adjusts fan speed based on CPU temperature:
<45°C: Silent (25%)
45–60°C: Balanced (50%)
60–75°C: Performance (75%)

75°C: Turbo (100%)




System Tray: Close the window to minimize to a system tray icon (purple circle). Right-click to restore or exit.


Status Updates:

The GUI displays messages like "Manual Mode: Set fan speed to 50%" or "Failed to set fan speed."
Warnings appear if setup steps or fan configuration fail.



Troubleshooting

NBFC Setup Fails:

Check terminal output for details:sudo python3 laptop_fan_control.py | tee log.txt

Look at log.txt for errors (e.g., network issues, apt problems).
Ensure you have internet access and sudo privileges.
Verify NBFC installation:nbfc --version




No Fan Configurations Available:

Run:sudo nbfc config -l

If no configurations are listed, your laptop may not be supported. Check NBFC-Linux GitHub for supported models.


CPU Temperature Shows N/A:

Check hwmon paths:ls /sys/class/hwmon
cat /sys/class/hwmon/hwmon*/name

Edit the get_cpu_temp function in the script to use the correct hwmon path (e.g., hwmon0).


Fan Control Doesn’t Work:

Confirm NBFC is installed and configured:sudo nbfc status


Rerun with sudo:sudo python3 laptop_fan_control.py


Ensure a valid fan configuration was applied.


Permission Issues:

If sudo prompts cause problems, configure passwordless sudo (use with caution):sudo visudo

Add:your_username ALL=(ALL) NOPASSWD: /usr/bin/nbfc, /usr/bin/apt





Customization

System Tray Icon:Change the purple circle icon in the create_image function:
image = Image.open("path/to/icon.png")


Fan Speeds and Temperatures:Adjust the fan_modes dictionary or auto_mode_loop function to change speed percentages or temperature thresholds.

GUI Appearance:Modify bg, fg, activebackground, and selectcolor in the GUI elements to customize the color scheme (currently Dracula-themed).


Contributing

Fork the repository.
Create a feature branch:git checkout -b feature/your-feature


Commit your changes:git commit -m "Add your feature"


Push to the branch:git push origin feature/your-feature


Open a pull request on GitHub.

License
This project is licensed under the MIT License. See the LICENSE file for details.
Acknowledgments

NBFC-Linux for providing fan control functionality.
Dracula Theme for inspiring the GUI colors.


For bugs or feature requests, please open an issue on the GitHub repository.
