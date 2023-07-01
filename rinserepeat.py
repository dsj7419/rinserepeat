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
    root.mainloop()

if __name__ == "__main__":
    main()
