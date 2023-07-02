import random
import string
import subprocess
import wmi
import os
import ctypes
import psutil
from tkinter import messagebox
from tkinter import Tk, Button, Toplevel, Text

class RinseRepeat:
    def __init__(self):
        self.root = Tk()
        self.root.withdraw()

        self.analysis_results = self.analyze_system()

        self.analysis_window = Toplevel(self.root)
        self.analysis_window.title("RinseRepeat")
        self.analysis_window.configure(bg="black")

        self.analysis_text = Text(self.analysis_window, bg="black", fg="red")
        for result in self.analysis_results:
            self.analysis_text.insert('end', result + "\n")
        self.analysis_text.pack()

        self.proceed_button = Button(self.analysis_window, text="Proceed", command=self.proceed, bg="red", fg="white")
        self.proceed_button.pack(side="left", padx=10, pady=10)

        self.cancel_button = Button(self.analysis_window, text="Cancel", command=self.cancel_changes, bg="red",
                                    fg="white")
        self.cancel_button.pack(side="right", padx=10, pady=10)

        # Initialize instance variables to hold original values
        self.registry_key_original = None
        self.computer_name_original = None
        self.mac_address_original = None
        self.pagefile_size_original = None

    def generate_random_string(self, length):
        characters = string.hexdigits[:16]  # 0-9 and A-F/a-f
        return ''.join(random.choice(characters) for _ in range(length))

    def check_registry_key(self):
        result = subprocess.run(
            ['reg', 'query', 'HKEY_CURRENT_USER\Software\Blizzard Entertainment\Battle.net\Identity'],
            capture_output=True)
        if result.returncode == 0:
            self.registry_key_original = "Located!"  # Key exists
            return "Registry Key: Located!"
        else:
            self.registry_key_original = "Not found"  # Key does not exist
            return "Registry Key: Not found"

    def check_computer_name(self):
        c = wmi.WMI()
        computer = c.Win32_ComputerSystem()[0]
        self.computer_name_original = computer.Name
        current_name = self.computer_name_original

        prefix = current_name.split("-")[0]  # Use the first part of the current name as a prefix
        suffix = self.generate_random_string(5).upper()  # Generate a random 5-character suffix

        new_name = prefix + "-" + suffix

        return f"Computer Name: Current: {current_name}\n   Target: {new_name}"

    def check_mac_address(self):
        c = wmi.WMI()
        network_adapters = c.Win32_NetworkAdapterConfiguration(IPEnabled=True)
        mac_addresses = []
        for adapter in network_adapters:
            if adapter.MACAddress:
                mac_addresses.append(adapter.MACAddress)
        if mac_addresses:
            self.mac_address_original = mac_addresses[0]
            target_mac = ":".join([self.generate_random_string(2).upper() for _ in range(6)])
            return f"MAC Address:\n   Current:\n      " + "\n      ".join(mac_addresses) + f"\n   Target: {target_mac}"
        else:
            self.mac_address_original = None
            return "MAC Address: No MAC addresses found"

    def check_pagefile_size(self):
        pagefile_info = {}

        for partition in psutil.disk_partitions():
            if os.name == "nt" and partition.device.startswith("C:") and "fixed" in partition.opts:
                current_size = psutil.swap_memory().total // (1024 * 1024)  # Convert to MB
                target_size = random.randint(current_size - 512,
                                             current_size + 512)  # Slightly above or below current size
                pagefile_info[partition.device] = {
                    "current_size": current_size,
                    "target_size": target_size
                }

        result = ""
        for partition, sizes in pagefile_info.items():
            result += f"{partition}:\n   Current Size: {sizes['current_size']}MB\n   Target Size: {sizes['target_size']}MB\n"

        self.pagefile_size_original = pagefile_info
        return result

    def analyze_system(self):
        analysis_results = []

        analysis_results.append(self.check_registry_key())
        analysis_results.append(self.check_computer_name())
        analysis_results.append(self.check_mac_address())
        analysis_results.append(self.check_pagefile_size())

        return analysis_results

    def cancel_changes(self, window):
        # Display a confirmation dialog
        if messagebox.askyesno("Confirmation", "Are you sure you want to cancel?"):
            # Destroy the window and exit the script
            window.destroy()
            os._exit(0)  # Terminate the script immediately

    def proceed(self):
        self.analysis_window.destroy()
        proceed_window = Toplevel(self.root)
        proceed_window.title("Confirmation")
        proceed_window.configure(bg="black")

        confirmation_text = Text(proceed_window, bg="black", fg="red")
        confirmation_text.insert('end', "Are you sure you want to proceed with the changes?\n")
        confirmation_text.insert('end', "This action may have irreversible effects.\n")
        for result in self.analysis_results:
            if "Change is likely to succeed. Target" in result:
                confirmation_text.insert('end', result.split("Target:")[1].strip() + "\n")
        confirmation_text.pack()

        def execute_changes():
            proceed_window.destroy()

            results = []
            results.append(self.change_registry_key())
            results.append(self.change_computer_name(new_name))
            results.append(self.change_mac_address(target_mac))
            results.append(self.change_pagefile_size(target_size))

            summary_window = Toplevel(self.root)
            summary_window.title("Operation Summary")
            summary_window.configure(bg="black")

            summary_text = Text(summary_window, bg="black", fg="red")
            for result in results:
                summary_text.insert('end', result + "\n")
            summary_text.pack()

            def revert_changes():
                self.revert_changes()
                summary_text.delete(1.0, 'end')
                summary_text.insert('end', "Changes successfully reverted.")

            def reboot():
                os.system("shutdown /r /t 1")

            self.revert_button = Button(summary_window, text="Revert Changes", command=self.revert_changes, bg="red",
                                        fg="white")
            self.revert_button.pack(side="left", padx=10, pady=10)

            reboot_button = Button(summary_window, text="Reboot Now", command=reboot, bg="red", fg="white")
            reboot_button.pack(side="left", padx=10, pady=10)

            self.cancel_button = Button(summary_window, text="Cancel",
                                        command=lambda: self.cancel_changes(summary_window), bg="red", fg="white")
            self.cancel_button.pack(side="right", padx=10, pady=10)

        proceed_button = Button(proceed_window, text="Proceed", command=execute_changes, bg="red", fg="white")
        proceed_button.pack(side="left", padx=10, pady=10)

        self.cancel_button = Button(proceed_window, text="Cancel", command=lambda: self.cancel_changes(proceed_window),
                                    bg="red", fg="white")
        self.cancel_button.pack(side="right", padx=10, pady=10)

    def change_registry_key(self):
        try:
            subprocess.run(
                ['reg', 'delete', 'HKEY_CURRENT_USER\Software\Blizzard Entertainment\Battle.net\Identity', '/f'])
            return "Registry Key: Delete successful"
        except Exception as e:
            return f"Registry Key: Delete failed - {str(e)}"

    def change_computer_name(self, new_name):
        try:
            c = wmi.WMI()
            computer = c.Win32_ComputerSystem()[0]
            computer.Rename(new_name)  # Replace "NewComputerName" with the desired name
            return f"Computer Name: Changed to {new_name}"
        except Exception as e:
            return f"Computer Name: Change failed - {str(e)}"

    def change_mac_address(self, target_mac):
        try:
            c = wmi.WMI()
            network_adapters = c.Win32_NetworkAdapterConfiguration(IPEnabled=True)
            for adapter in network_adapters:
                if adapter.MACAddress:
                    adapter.MACAddress = target_mac
                    adapter.Put_()
            return "MAC Address: Changed successfully"
        except Exception as e:
            return f"MAC Address: Change failed - {str(e)}"

    def change_pagefile_size(self, target_size):
        try:
            for partition, sizes in self.pagefile_size_original.items():
                # Modify the pagefile size using the 'wmic' command
                subprocess.run(['wmic', 'pagefileset', 'where', f'name="{partition}\\pagefile.sys"', 'set',
                                f'InitialSize={target_size}', 'MaximumSize={target_size}'], capture_output=True,
                               text=True, check=True)

            return "Pagefile Size: Changed successfully"
        except Exception as e:
            return f"Pagefile Size: Change failed - {str(e)}"

    def revert_changes(self):
        results = []

        if self.computer_name_original is not None:
            results.append(self.change_computer_name(self.computer_name_original))

        if self.mac_address_original is not None:
            results.append(self.change_mac_address(self.mac_address_original))

        if self.pagefile_size_original is not None:
            for partition, sizes in self.pagefile_size_original.items():
                target_size = sizes['current_size']
                results.append(self.change_pagefile_size(target_size))

        # Update the summary text
        summary_text = self.summary_text
        summary_text.delete(1.0, 'end')
        for result in results:
            summary_text.insert('end', result + "\n")

        # Add a message to indicate that changes have been reverted
        summary_text.insert('end', "\nChanges successfully reverted.")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    RinseRepeat().run()
