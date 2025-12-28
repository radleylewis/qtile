#!/usr/bin/env python3

import subprocess
import sys
import re
import time
from typing import List, Tuple

from utils import notify

DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
BACK_BUTTON = "Back"


class BluetoothManager:
    def __init__(self, rofi_args: List[str] = []):
        self.rofi_args = rofi_args or []

    def _run_command(self, command: List[str]) -> str:
        """Run generic command and return output"""
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError:
            return ""

    def run_bluetoothctl(self, command: str) -> str:
        """Run bluetoothctl command and return output"""
        try:
            if isinstance(command, str):
                cmd = ["bluetoothctl"] + command.split()
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError:
            return ""

    def power_on(self) -> bool:
        """Checks if bluetooth controller is powered on"""
        output = self.run_bluetoothctl("show")
        return "Powered: yes" in output

    def toggle_power(self):
        """Toggles power state"""
        if self.power_on():
            self.run_bluetoothctl("power off")
            self.show_menu()
        else:
            rfkill_output = self._run_command(["rfkill", "list", "bluetooth"])
            if "blocked: yes" in rfkill_output:
                subprocess.run(["rfkill", "unblock", "bluetooth"])
                time.sleep(3)
            self.run_bluetoothctl("power on")
            self.show_menu()

    def scan_on(self) -> Tuple[str, bool]:
        """Checks if controller is scanning for new devices"""
        output = self.run_bluetoothctl("show")
        if "Discovering: yes" in output:
            return "Scan: on", True
        else:
            return "Scan: off", False

    def toggle_scan(self):
        """Toggles scanning state"""
        _, is_scanning = self.scan_on()
        if is_scanning:
            # Kill existing scan processes
            try:
                subprocess.run(["pkill", "-f", "bluetoothctl --timeout 5 scan on"])
            except subprocess.CalledProcessError:
                pass
            self.run_bluetoothctl("scan off")
            notify("Bluetooth", "Scanning stopped")
            self.show_menu()
        else:
            # Start scanning in background
            subprocess.Popen(["bluetoothctl", "--timeout", "5", "scan", "on"])
            notify("Bluetooth", "Scanning for devices...")
            self.show_menu()

    def pairable_on(self) -> Tuple[str, bool]:
        """Checks if controller is able to pair to devices"""
        output = self.run_bluetoothctl("show")
        if "Pairable: yes" in output:
            return "Pairable: on", True
        else:
            return "Pairable: off", False

    def toggle_pairable(self):
        """Toggles pairable state"""
        _, is_pairable = self.pairable_on()
        if is_pairable:
            self.run_bluetoothctl("pairable off")
        else:
            self.run_bluetoothctl("pairable on")
        self.show_menu()

    def discoverable_on(self) -> Tuple[str, bool]:
        """Checks if controller is discoverable by other devices"""
        output = self.run_bluetoothctl("show")
        if "Discoverable: yes" in output:
            return "Discoverable: on", True
        else:
            return "Discoverable: off", False

    def toggle_discoverable(self):
        """Toggles discoverable state"""
        _, is_discoverable = self.discoverable_on()
        if is_discoverable:
            self.run_bluetoothctl("discoverable off")
        else:
            self.run_bluetoothctl("discoverable on")
        self.show_menu()

    def device_connected(self, mac: str) -> bool:
        """Checks if a device is connected"""
        device_info = self.run_bluetoothctl(f"info {mac}")
        return "Connected: yes" in device_info

    def toggle_connection(self, mac: str, device: str):
        """Toggles device connection"""
        if self.device_connected(mac):
            self.run_bluetoothctl(f"disconnect {mac}")
        else:
            self.run_bluetoothctl(f"connect {mac}")
        self.device_menu(device)

    def device_paired(self, mac: str) -> Tuple[str, bool]:
        """Checks if a device is paired"""
        device_info = self.run_bluetoothctl(f"info {mac}")
        if "Paired: yes" in device_info:
            return "Paired: yes", True
        else:
            return "Paired: no", False

    def toggle_paired(self, mac: str, device: str):
        """Toggles device paired state"""
        _, is_paired = self.device_paired(mac)
        if is_paired:
            self.run_bluetoothctl(f"remove {mac}")
        else:
            # Use a more robust pairing method
            try:
                subprocess.run(["bluetoothctl", "agent", "NoInputNoOutput"], timeout=5)
                subprocess.run(["bluetoothctl", "default-agent"], timeout=5)
                subprocess.run(["bluetoothctl", "pair", mac], timeout=30)
                subprocess.run(["bluetoothctl", "trust", mac], timeout=5)
            except subprocess.TimeoutExpired:
                notify("Bluetooth", "Pairing timeout", urgency="critical")
        self.device_menu(device)

    def device_trusted(self, mac: str) -> Tuple[str, bool]:
        """Checks if a device is trusted"""
        device_info = self.run_bluetoothctl(f"info {mac}")
        if "Trusted: yes" in device_info:
            return "Trusted: yes", True
        else:
            return "Trusted: no", False

    def toggle_trust(self, mac: str, device: str):
        """Toggles device trust state"""
        _, is_trusted = self.device_trusted(mac)
        if is_trusted:
            self.run_bluetoothctl(f"untrust {mac}")
        else:
            self.run_bluetoothctl(f"trust {mac}")
        self.device_menu(device)

    def get_bluetoothctl_version(self) -> float:
        """Get bluetoothctl version for backwards compatibility"""
        try:
            output = self.run_bluetoothctl("version")
            version_match = re.search(r"(\d+\.\d+)", output)
            if version_match:
                return float(version_match.group(1))
            return 5.65  # Default to newer version if can't parse
        except Exception:
            return 5.65

    def print_status(self):
        """Prints a short string with the current bluetooth status"""
        if self.power_on():
            print("", end="")

            # Check bluetoothctl version for backwards compatibility
            version = self.get_bluetoothctl_version()
            if version < 5.65:
                paired_devices_cmd = "paired-devices"
            else:
                paired_devices_cmd = "devices Paired"

            paired_devices_output = self.run_bluetoothctl(paired_devices_cmd)
            paired_devices = []
            for line in paired_devices_output.split("\n"):
                if "Device" in line:
                    mac = line.split()[1]
                    paired_devices.append(mac)

            connected_devices = []
            for device_mac in paired_devices:
                if self.device_connected(device_mac):
                    device_info = self.run_bluetoothctl(f"info {device_mac}")
                    for line in device_info.split("\n"):
                        if "Alias" in line:
                            alias = " ".join(line.split()[1:])
                            connected_devices.append(alias)
                            break

            if connected_devices:
                print(" " + ", ".join(connected_devices))
            else:
                print()
        else:
            print("")

    def rofi_menu(self, options: str, prompt: str) -> str:
        """Display rofi menu and return selected option"""
        cmd = ["rofi", "-dmenu"] + self.rofi_args + ["-p", prompt]
        try:
            result = subprocess.run(cmd, input=options, text=True, capture_output=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""

    def device_menu(self, device: str):
        """A submenu for a specific device that allows connecting, pairing, and trusting"""
        # Parse device string: "Device XX:XX:XX:XX:XX:XX Device Name"
        parts = device.split()
        if len(parts) < 3:
            return

        mac = parts[1]
        device_name = " ".join(parts[2:])

        # Build options
        if self.device_connected(mac):
            connected = "Connected: yes"
        else:
            connected = "Connected: no"

        paired, _ = self.device_paired(mac)
        trusted, _ = self.device_trusted(mac)

        options = (
            f"{connected}\n{paired}\n{trusted}\nRemove\n{DIVIDER}\n{BACK_BUTTON}\nExit"
        )

        # Open rofi menu
        chosen = self.rofi_menu(options, device_name)

        # Match chosen option to command
        if chosen == "" or chosen == DIVIDER:
            print("No option chosen.")
        elif chosen == connected:
            self.toggle_connection(mac, device)
        elif chosen == paired:
            self.toggle_paired(mac, device)
        elif chosen == trusted:
            self.toggle_trust(mac, device)
        elif chosen == "Remove":
            self.run_bluetoothctl(f"remove {mac}")
            notify("Bluetooth", f"Removed {device_name}")
            self.show_menu()  # Go back to main menu after removal
        elif chosen == BACK_BUTTON:
            self.show_menu()

    def show_menu(self):
        """Opens a rofi menu with current bluetooth status and options to connect"""
        if self.power_on():
            power = "Power: on"

            # Get devices
            devices_output = self.run_bluetoothctl("devices")
            devices = []
            for line in devices_output.split("\n"):
                if "Device" in line:
                    # Extract device name (everything after MAC address)
                    parts = line.split()
                    if len(parts) >= 3:
                        device_name = " ".join(parts[2:])
                        devices.append(device_name)

            # Get controller flags
            scan, _ = self.scan_on()
            pairable, _ = self.pairable_on()
            discoverable, _ = self.discoverable_on()

            # Build options
            device_list = "\n".join(devices) if devices else ""
            if device_list:
                options = f"{power}\n{scan}\n{pairable}\n{discoverable}\nExit\n{DIVIDER}\n{device_list}"
            else:
                options = (
                    f"{DIVIDER}\n{power}\n{scan}\n{pairable}\n{discoverable}\nExit"
                )
        else:
            power = "Power: off"
            options = f"{power}\nExit"

        # Open rofi menu
        chosen = self.rofi_menu(options, "")

        # Match chosen option to command
        if chosen == "" or chosen == DIVIDER:
            print("No option chosen.")
        elif chosen == power:
            self.toggle_power()
        elif chosen.startswith("Scan:"):
            self.toggle_scan()
        elif chosen.startswith("Discoverable:"):
            self.toggle_discoverable()
        elif chosen.startswith("Pairable:"):
            self.toggle_pairable()
        elif chosen == "Exit":
            sys.exit(0)
        else:
            # Check if it's a device
            devices_output = self.run_bluetoothctl("devices")
            for line in devices_output.split("\n"):
                if "Device" in line and chosen in line:
                    self.device_menu(line)
                    break


def main():
    # Parse command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        bt_manager = BluetoothManager()
        bt_manager.print_status()
    else:
        # Pass any additional arguments to rofi
        rofi_args = sys.argv[1:] if len(sys.argv) > 1 else []
        bt_manager = BluetoothManager(rofi_args)
        bt_manager.show_menu()


if __name__ == "__main__":
    main()
