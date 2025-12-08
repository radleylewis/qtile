#!/usr/bin/env python3

import subprocess
from libqtile.lazy import lazy


def get_brightness():
    """Return brightness level (0–100)."""
    result = subprocess.run(
        ["brightnessctl", "g"], capture_output=True, text=True, check=True
    )
    current = int(result.stdout.strip())

    result_max = subprocess.run(
        ["brightnessctl", "m"], capture_output=True, text=True, check=True
    )
    maximum = int(result_max.stdout.strip())

    percent = round((current / maximum) * 100)
    return percent


def send_brightness_notification(brightness):
    """Show brightness notification via mako/notify-send."""
    icon = "🔅" if brightness < 50 else "🔆"

    bar_len = 20
    filled = int((brightness / 100) * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)

    body = f"{icon} Brightness: {brightness}%\n{bar}"

    subprocess.Popen(
        [
            "notify-send",
            "--app-name=brightness-control",
            "--replace-id=3000",
            "--expire-time=1200",
            "Screen Brightness",
            body,
        ]
    )


@lazy.function
def increase_brightness(_qtile, amount=5):  # FIXED
    subprocess.run(["brightnessctl", "set", f"{amount}%+"], check=True)
    brightness = get_brightness()
    send_brightness_notification(brightness)


@lazy.function
def decrease_brightness(_qtile, amount=5):  # FIXED
    subprocess.run(["brightnessctl", "set", f"{amount}%-"], check=True)
    brightness = get_brightness()
    send_brightness_notification(brightness)
