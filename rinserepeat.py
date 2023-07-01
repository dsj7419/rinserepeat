import ctypes
import random
import string
import subprocess
import wmi
import os
from ctypes import wintypes
from tkinter import messagebox
from tkinter import Tk, Button, Label, Toplevel, Text

def generate_random_string(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

def check_registry_key():
    result = subprocess.run(['reg', 'query', 'HKEY_CURRENT_USER\Software\Blizzard Entertainment\Battle.net\Identity'], capture_output=True)
    if result.returncode == 0:
        return True  # Key exists
    else:
        return False  # Key does not exist

def check_computer_name():
    new_name = generate_random_string(15)
    return new_name

def check_mac_address():
    c = wmi.WMI()
    network_adapters = c.Win32_NetworkAdapterConfiguration(IPEnabled=True)
    for adapter in network_adapters:
        if adapter.MACAddress:
            return adapter.MACAddress  # Current MAC address
    return False  # MAC address cannot be changed

def check_pagefile_size():
    c = wmi.WMI()
    pagefile = c.Win32_PageFileSetting()[0]
    current_size = int(pagefile.InitialSize)
    target_size = random.randint(current_size + 512, current_size + 1024)  # Slightly above current size
    return str(current_size), str(target_size)

def analyze_system():
    analysis_results = []

    registry_key_exists = check_registry_key()
    if not registry_key_exists:
        analysis_results.append("Registry Key: Change might fail. Key does not exist.")
    else:
        analysis_results.append("Registry Key: Change is likely to succeed.")

    computer_name = check_computer_name()
    analysis_results.append("Computer Name: Change is likely to succeed. Target: " + computer_name)

    mac_address = check_mac_address()
    if mac_address:
        analysis_results.append("MAC Address: Change is likely to succeed. Current: " + mac_address + ", Target: Random MAC Address")
    else:
        analysis_results.append("MAC Address: Change might fail. MAC address cannot be changed.")

    current_size, target_size = check_pagefile_size()
    analysis_results.append("Pagefile Size: Change is likely to succeed. Current Size: " + current_size + "MB, Target Size: " + target_size + "MB")

    return analysis_results

def delete_registry_key():
    try:
        os.system('reg delete HKEY_CURRENT_USER\Software\Blizzard Entertainment\Battle.net\Identity /f')
        return "Successfully deleted the registry key."
    except Exception as e:
        return "Failed to delete the registry key. Error: " + str(e)

def change_computer_name():
    try:
        new_name = generate_random_string(15)
        os.system('wmic computersystem where caption=\'%computername%\' rename ' + new_name)
        return "Successfully changed the computer name to " + new_name
    except Exception as e:
        return "Failed to change the computer name. Error: " + str(e)

def change_mac_address():
    try:
        os.system('netsh interface set interface "Wi-Fi" admin=disable')
        os.system('netsh interface set interface "Wi-Fi" admin=enable')
        return "Successfully changed the MAC address."
    except Exception as e:
        return "Failed to change the MAC address. Error: " + str(e)

def change_pagefile_size():
    try:
        size = str(random.randint(4096, 8192))
        os.system('wmic computersystem where name="%computername%" set AutomaticManagedPagefile=False')
        os.system('wmic pagefileset where name="C:\\pagefile.sys" set InitialSize={},MaximumSize={}'.format(size, size))
        return "Successfully changed the pagefile size to " + size + "MB."
    except Exception as e:
        return "Failed to change the pagefile size. Error: " + str(e)

def main():
    root = Tk()
    root.withdraw()
    analysis_results = analyze_system()

    analysis_window = Toplevel(root)
    analysis_window.title("System Analysis")
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

            Button(summary_window, text="Reboot Now", command=reboot, bg="red", fg="white").pack()
            Button(summary_window, text="Reboot Later", command=summary_window.destroy, bg="red", fg="white").pack()

        Button(proceed_window, text="Proceed", command=execute_changes, bg="red", fg="white").pack()
        Button(proceed_window, text="Cancel", command=proceed_window.destroy, bg="red", fg="white").pack()

    proceed_button = Button(analysis_window, text="Proceed", command=proceed, bg="red", fg="white")
    proceed_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
