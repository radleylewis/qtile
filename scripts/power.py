#!/usr/bin/env python3

import subprocess
import os
from typing import List

shutdown_icon = ""
reboot_icon = ""
sleep_icon = "󰤄"
lock_icon = ""
logout_icon = "󰗽"
yes_icon = ""
no_icon = ""

config_dir = os.environ.get("XDG_CONFIG_HOME", "") + "/rofi"


def get_uptime() -> str:
    result = subprocess.run(["uptime", "-p"], capture_output=True, text=True)
    return result.stdout.strip().replace("up ", "")


def main_menu() -> str:
    options: List[str] = [
        lock_icon,
        logout_icon,
        sleep_icon,
        shutdown_icon,
        reboot_icon,
    ]
    menu: str = "\n".join([f"{item}" for item in options])
    uptime = get_uptime()
    result = subprocess.run(
        [
            "rofi",
            "-dmenu",
            "-p",
            f"Uptime: {uptime}",
            "-mesg",
            f"Uptime: {uptime}",
            "-theme",
            f"{config_dir}/power.rasi",
        ],
        input=menu,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return result.split("\n")[0]


def confirm() -> bool:
    options = [yes_icon, no_icon]
    menu: str = "\n".join([f"{item}" for item in options])
    result = subprocess.run(
        [
            "rofi",
            "-theme",
            f"{config_dir}/power.rasi",
            "-theme-str",
            "listview {columns: 2; lines: 1;}",
            "-dmenu",
            "-p",
            "Confirmation",
            "-mesg",
            "Confirm?",
        ],
        input=menu,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return result == yes_icon


def lock_qtile():
    subprocess.Popen(
        [
            "swaylock",
            "-i",
            "~/.config/qtile/assets/wallpapers/lock_screen.png",
            "--clock",
        ]
    )


def sleep():
    script_path = os.path.expanduser("~/.config/qtile/scripts/sleep.sh")
    subprocess.Popen([script_path])


def power():
    selected = main_menu()

    if selected == lock_icon:
        lock_qtile()
    elif selected == sleep_icon:
        sleep()
    else:
        action_map = {
            shutdown_icon: ["systemctl", "poweroff"],
            reboot_icon: ["systemctl", "reboot"],
            logout_icon: ["pkill", "-KILL", "-u", os.environ["USER"]],
        }

        if action := action_map[selected]:
            if confirm():
                subprocess.run(action)


if __name__ == "__main__":
    power()
