import subprocess
import re
from libqtile.lazy import lazy


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────


def notify(title: str, body: str, urgency: str = "normal", replaces_id: str = ""):
    """Wrapper around notify-send (for mako)"""
    cmd = ["notify-send", "-u", urgency]

    if replaces_id:
        cmd.extend(["-r", replaces_id])

    cmd.extend([title, body])
    subprocess.run(cmd, check=False)


# ─────────────────────────────────────────────
#  Microphone
# ─────────────────────────────────────────────


def get_mic_status():
    """Return True if mic is muted"""
    try:
        result = subprocess.run(
            ["pactl", "get-source-mute", "@DEFAULT_SOURCE@"],
            capture_output=True,
            text=True,
            check=True,
        )
        return "yes" in result.stdout.lower()
    except subprocess.CalledProcessError:
        return True


def send_mic_notification(is_muted: bool):
    """Show a mako notification for mic state"""
    if is_muted:
        notify(
            "Microphone",
            "🎤❌ Microphone Muted",
            urgency="normal",
            replaces_id="2000",
        )
    else:
        notify(
            "Microphone",
            "🎤 Microphone Live",
            urgency="critical",  # red warning when mic is hot
            replaces_id="2000",
        )


@lazy.function
def toggle_mute_audio_input(qtile):
    """Toggle microphone mute"""
    try:
        subprocess.run(
            ["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "toggle"], check=True
        )
        send_mic_notification(get_mic_status())

    except subprocess.CalledProcessError:
        notify("Microphone Error", "Could not toggle mic", urgency="critical")


# ─────────────────────────────────────────────
#  Volume (Output Audio)
# ─────────────────────────────────────────────


def get_default_sink():
    try:
        result = subprocess.run(
            ["pactl", "get-default-sink"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def get_volume():
    """Return (volume %, is_muted)"""
    sink = get_default_sink()
    if not sink:
        return 0, False

    try:
        v = subprocess.run(
            ["pactl", "get-sink-volume", sink],
            capture_output=True,
            text=True,
            check=True,
        )

        m = subprocess.run(
            ["pactl", "get-sink-mute", sink], capture_output=True, text=True, check=True
        )

        volume_match = re.search(r"/\s*(\d+)%", v.stdout)
        volume = int(volume_match.group(1)) if volume_match else 0

        muted = "yes" in m.stdout
        return volume, muted

    except subprocess.CalledProcessError:
        return 0, False


def send_volume_notification(volume: int, is_muted: bool):
    """Show volume notification with bar"""
    if is_muted:
        icon = "🔇"
        message = f"Volume Muted ({volume}%)"
        urgency = "normal"
    else:
        icon = "🔈" if volume == 0 else "🔉" if volume < 50 else "🔊"
        message = f"Volume: {volume}%"
        urgency = "low"

    bar_length = 20
    filled = int(volume / 100 * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)

    notify(
        "Volume",
        f"{icon} {message}\n{bar}",
        urgency=urgency,
        replaces_id="1000",
    )


# ─────────────────────────────────────────────
#  Qtile Bindings
# ─────────────────────────────────────────────


@lazy.function
def raise_volume(qtile):
    """Increase volume"""
    sink = get_default_sink()
    if not sink:
        return

    subprocess.run(["pactl", "set-sink-volume", sink, "+5%"])
    volume, muted = get_volume()
    send_volume_notification(volume, muted)


@lazy.function
def lower_volume(qtile):
    """Decrease volume"""
    sink = get_default_sink()
    if not sink:
        return

    subprocess.run(["pactl", "set-sink-volume", sink, "-5%"])
    volume, muted = get_volume()
    send_volume_notification(volume, muted)


@lazy.function
def toggle_mute_audio_output(qtile):
    """Mute/unmute speakers"""
    sink = get_default_sink()
    if not sink:
        return

    subprocess.run(["pactl", "set-sink-mute", sink, "toggle"])
    volume, muted = get_volume()
    send_volume_notification(volume, muted)
