import ctypes
import random
import string
import subprocess
import wmi
import os
import psutil
from ctypes import wintypes
from tkinter import messagebox
from tkinter import Tk, Button, Label, Toplevel, Text

def generate_random_string(length):
    characters = string.hexdigits[:16]  # 0-9 and A-F/a-f
    return ''.join(random.choice(characters) for _ in range(length))

def check_registry_key():
    result = subprocess.run(['reg', 'query', 'HKEY_CURRENT_USER\Software\Blizzard Entertainment\Battle.net\Identity'], capture_output=True)
    if result.returncode == 0:
        return "Registry Key: Located!"  # Key exists
    else:
        return "Registry Key: Not found"  # Key does not exist

def check_computer_name():
    c = wmi.WMI()
    computer = c.Win32_ComputerSystem()[0]
    current_name = computer.Name

    prefix = current_name.split("-")[0]  # Use the first part of the current name as a prefix
    suffix = generate_random_string(5).upper()  # Generate a random 5-character suffix

    new_name = prefix + "-" + suffix

    return f"Computer Name: Current: {current_name}\n   Target: {new_name}"

def check_mac_address():
    c = wmi.WMI()
    network_adapters = c.Win32_NetworkAdapterConfiguration(IPEnabled=True)
    mac_addresses = []
    for adapter in network_adapters:
        if adapter.MACAddress:
            mac_addresses.append(adapter.MACAddress)
    if mac_addresses:
        target_mac = ":".join([generate_random_string(2).upper() for _ in range(6)])
        return f"MAC Address:\n   Current:\n      " + "\n      ".join(mac_addresses) + f"\n   Target: {target_mac}"
    else:
        return "MAC Address: No MAC addresses found"

def check_pagefile_size():
    pagefile_info = {}

    for partition in psutil.disk_partitions():
        if os.name == "nt" and partition.device.startswith("C:") and "fixed" in partition.opts:
            current_size = psutil.swap_memory().total // (1024 * 1024)  # Convert to MB
            target_size = random.randint(current_size - 512, current_size + 512)  # Slightly above or below current size
            pagefile_info[partition.device] = {
                "current_size": current_size,
                "target_size": target_size
            }

    result = ""
    for partition, sizes in pagefile_info.items():
        result += f"{partition}:\n   Current Size: {sizes['current_size']}MB\n   Target Size: {sizes['target_size']}MB\n"

    return result

def analyze_system():
    analysis_results = []

    analysis_results.append(check_registry_key())
    analysis_results.append(check_computer_name())
    analysis_results.append(check_mac_address())
    analysis_results.append(check_pagefile_size())

    return analysis_results

def cancel_changes(window):
    # Display a confirmation dialog
    if messagebox.askyesno("Confirmation", "Are you sure you want to cancel?"):
        # Destroy the window and exit the script
        window.destroy()
        os._exit(0)  # Terminate the script immediately

def main():
    root = Tk()
    root.withdraw()
    analysis_results = analyze_system()

    analysis_window = Toplevel(root)
    analysis_window.title("RinseRepeat")
    analysis_window.configure(bg="black")

    analysis_text = Text(analysis_window, bg="black", fg="red")
    for result in analysis_results:
        analysis_text.insert('end', result + "\n")
    analysis_text.pack()

    def proceed():
        analysis_window.destroy()
        proceed_window = Toplevel(root)
        proceed_window.title("Confirmation")
        proceed_window.configure(bg="black")

        confirmation_text = Text(proceed_window, bg="black", fg="red")
        confirmation_text.insert('end', "Are you sure you want to proceed with the changes?\n")
        confirmation_text.insert('end', "This action may have irreversible effects.\n")
        for result in analysis_results:
            if "Change is likely to succeed. Target" in result:
                confirmation_text.insert('end', result.split("Target:")[1].strip() + "\n")
        confirmation_text.pack()

        def execute_changes():
            proceed_window.destroy()

            results = []
            results.append(delete_registry_key())
            results.append(change_computer_name())
            results.append(change_mac_address())
            results.append(change_pagefile_size())

            summary_window = Toplevel(root)
            summary_window.title("Operation Summary")
            summary_window.configure(bg="black")

            summary_text = Text(summary_window, bg="black", fg="red")
            for result in results:
                summary_text.insert('end', result + "\n")
            summary_text.pack()

            def reboot():
                os.system("shutdown /r /t 1")

            Button(summary_window, text="Reboot Now", command=reboot, bg="red", fg="white").pack(side="left", padx=10, pady=10)
            Button(summary_window, text="Cancel", command=lambda: cancel_changes(summary_window), bg="red", fg="white").pack(side="right", padx=10, pady=10)

        Button(proceed_window, text="Proceed", command=execute_changes, bg="red", fg="white").pack(side="left", padx=10, pady=10)
        Button(proceed_window, text="Cancel", command=lambda: cancel_changes(proceed_window), bg="red", fg="white").pack(side="right", padx=10, pady=10)

    Button(analysis_window, text="Proceed", command=proceed, bg="red", fg="white").pack(side="left", padx=10, pady=10)
    Button(analysis_window, text="Cancel", command=lambda: cancel_changes(analysis_window), bg="red", fg="white").pack(side="right", padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
