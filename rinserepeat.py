import ctypes
import os
import random
import string
import winreg
import subprocess
import wmi  # to install this library use: pip install WMI

def message_box(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

def delete_reg_key(path, key):
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        k = winreg.OpenKey(reg, path, 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteKey(k, key)
        message_box("Success", "Registry Key Deleted", 1)
    except WindowsError:
        message_box("Error", "Error while deleting key", 1)

def change_computer_name(new_name):
    os.system(f'WMIC computersystem where caption=\'%computername%\' rename {new_name}')
    message_box("Success", f"Computer name changed to {new_name}", 1)

def change_mac_address():
    try:
        interfaces = subprocess.check_output("netsh interface show interface", shell=True).decode()
        interface_name = None
        for line in interfaces.split('\n'):
            if "Disconnected" not in line and "Interface" not in line:
                interface_name = line.split()[-1]
                break
        if not interface_name:
            message_box("Error", "No active network interface found.", 1)
            return
        new_mac = ':'.join(['%02x' % random.randint(0, 255) for _ in range(6)])
        os.system(f'netsh interface set interface "{interface_name}" admin=disable')
        os.system(f'netsh interface set interface "{interface_name}" admin=enable')
        os.system(f'netsh interface set interface "{interface_name}" new_mac={new_mac}')
        message_box("Success", f"MAC Address Changed to {new_mac}", 1)
    except Exception as e:
        message_box("Error", f"Error while changing MAC: {e}", 1)

def change_pagefile_size(min_size, max_size):
    try:
        size = random.randint(min_size, max_size)
        wmi_obj = wmi.WMI ()
        for pagefile in wmi_obj.Win32_PageFileSetting():
            pagefile.InitialSize = size
            pagefile.MaximumSize = size
            pagefile.Put_()
        message_box("Success", f"Pagefile Size Changed to {size} MB", 1)
    except Exception as e:
        message_box("Error", f"Error while changing Pagefile size: {e}", 1)

delete_reg_key(r"Software\Blizzard Entertainment\Battle.net", "Identity")
new_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
change_computer_name(new_name)
change_mac_address()
change_pagefile_size(4096, 8192)
