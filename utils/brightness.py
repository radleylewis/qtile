import subprocess
import threading

from libqtile.lazy import lazy

from scripts.utils import notify


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
    icon = "󰖔" if brightness < 50 else "󰖙"

    bar_len = 35
    filled = int((brightness / 100) * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)

    title = "Screen Brightness"
    message = f"{icon} Brightness: {brightness}%\n{bar}"
    notify(title, message, app_name="brightness-control", tag="brightness")


@lazy.function
def increase_brightness(_qtile, amount=5):
    def _do():
        subprocess.run(["brightnessctl", "set", f"{amount}%+"])
        brightness = get_brightness()
        send_brightness_notification(brightness)

    threading.Thread(target=_do, daemon=True).start()


@lazy.function
def decrease_brightness(_qtile, amount=5):
    def _do():
        subprocess.run(["brightnessctl", "set", f"{amount}%-"])
        brightness = get_brightness()
        send_brightness_notification(brightness)

    threading.Thread(target=_do, daemon=True).start()
