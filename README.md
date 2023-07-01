# System Information Randomizer

This is a Python script, named `rinserepeat.py`, designed to randomize certain system-level properties on a Windows machine. The aim is to provide a level of system-level anonymity by changing identifiable properties.

## Features

- **Deletes a specific Registry Key**: The script deletes the `Identity` key from the `HKEY_CURRENT_USER\Software\Blizzard Entertainment\Battle.net` registry path.
- **Changes the Computer Name**: The script generates a random string of alphanumeric characters and changes the computer's name to this string.
- **Changes the MAC Address**: The script finds the active network interface and changes its MAC address to a randomly generated address.
- **Changes the Pagefile Size**: The script randomly sets the size of the system's pagefile within a specified range (e.g., 4096 to 8192 MB).

## Usage

1. **Python Installation**: Ensure that Python is installed on your machine. If not, you can download it from the [official Python website](https://www.python.org/downloads/).
2. **Install Required Libraries**: The script uses the `wmi` and `ctypes` Python libraries. You can install these libraries using pip:

pip install wmi ctypes

Run the Script: To run the script, navigate to the directory containing the script in your terminal and enter the command: python rinserepeat.py
   *Note: This script needs to be run with administrator privileges due to the nature of the operations it's performing.

Packaging as Executable
For easier distribution and usage, you can package this script as a standalone executable using PyInstaller:

pip install pyinstaller
pyinstaller --onefile rinserepeat.py

The resulting executable will be located in the dist folder.
Caution

This script performs significant system-level changes and should be used with caution. Users should clearly understand the changes it makes to their system and the potential risks involved. Additionally, the function to change the MAC address may not work on all network drivers, as many modern network drivers ignore or block attempts to change the MAC address. Always use such scripts responsibly and ensure that you have taken appropriate backups.


