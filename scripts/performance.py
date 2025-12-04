#!/usr/bin/env python3

import subprocess
import os
from typing import List

performance_icon = "󱓞"
balanced_icon = "󰓅"
quiet_icon = "󰁻"

yes_icon = ""
no_icon = ""

config_dir = os.environ.get("XDG_CONFIG_HOME", "") + "/rofi"


def get_current_profile() -> str:
    result = subprocess.run(
        [
            "asusctl", 
            "profile", 
            "-p", 
        ], capture_output=True, text=True)
    return result.stdout.splitlines()[1].split()[-1]

def performance_mode_menu() -> str:
    options = [
        ["Performance", performance_icon],
        ["Balanced", balanced_icon],
        ["Quiet", quiet_icon],
    ]
    menu: str = "\n".join([f"{icon} {mode}" for [mode, icon] in options])
    current_profile = get_current_profile()
    result = subprocess.run(
        [
            "rofi",
            "-dmenu",
            "-p",
            f"Current Profile: {current_profile}",
            "-mesg",
            f"Current Profile: {current_profile}",
            "-theme",
            f"{config_dir}/power.rasi",
            "-theme-str",
            "listview {columns: 3; lines: 1;}",
        ],
        input=menu,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return result.split()[1]


def confirm(mode: str) -> bool:
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
            f"Set to {mode} mode?",
        ],
        input=menu,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return result == yes_icon

def set_performance_profile():
    selection = performance_mode_menu()
    action = ["asusctl", "profile", "-P", selection]
    if confirm(selection):
        subprocess.run(action)


if __name__ == "__main__":
    set_performance_profile()
