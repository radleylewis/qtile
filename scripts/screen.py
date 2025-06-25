import subprocess
from libqtile.lazy import lazy


def get_brightness():
    """Get current brightness level using brillo"""
    try:
        result = subprocess.run(
            ["brillo", "-G"], capture_output=True, text=True, check=True
        )
        brightness = round(float(result.stdout.strip()))
        return brightness
    except subprocess.CalledProcessError:
        return 0


def send_brightness_notification(brightness):
    """Send notification with brightness level"""
    if brightness == 0:
        icon = "🔅"
    elif brightness < 25:
        icon = "🔅"
    elif brightness < 50:
        icon = "🔅"
    elif brightness < 75:
        icon = "🔆"
    else:
        icon = "🔆"

    message = f"Brightness: {brightness}%"

    # Create progress bar
    bar_length = 20
    filled = int((brightness / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)

    notification_body = f"{icon} {message}\n{bar}"

    subprocess.Popen(
        [
            "dunstify",
            "-a",
            "brightness-control",
            "-r",
            "3000",
            "-u",
            "low",
            "-t",
            "2000",
            "Screen Brightness",
            notification_body,
        ],
    )


@lazy.function
def increase_brightness(_qtile, amount=5):
    """Increase screen brightness with notification"""
    try:
        subprocess.Popen(["brillo", "-q", "-u", "200000", "-A", f"{amount}%"])

        brightness = get_brightness()
        send_brightness_notification(brightness)

    except subprocess.CalledProcessError:
        subprocess.Popen(
            [
                "dunstify",
                "-a",
                "brightness-control",
                "-u",
                "critical",
                "-t",
                "3000",
                "Brightness Error",
                "Could not increase brightness",
            ]
        )


@lazy.function
def decrease_brightness(qtile, amount=5):
    """Decrease screen brightness with notification"""
    try:
        subprocess.Popen(["brillo", "-q", "-u", "200000", "-U", f"{amount}%"])

        brightness = get_brightness()
        send_brightness_notification(brightness)

    except subprocess.CalledProcessError:
        subprocess.Popen(
            [
                "dunstify",
                "-a",
                "brightness-control",
                "-u",
                "critical",
                "-t",
                "3000",
                "Brightness Error",
                "Could not decrease brightness",
            ]
        )
