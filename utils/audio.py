import subprocess
import re
from libqtile.lazy import lazy
import threading

from assets.constants import Colours
from scripts.helpers import notify as _notify

SINK = "@DEFAULT_AUDIO_SINK@"
SOURCE = "@DEFAULT_AUDIO_SOURCE@"
MAX_VOLUME = 130  # percent


def notify(title: str, body: str, urgency: str = "normal", tag: str = ""):
    """Shared notify-send wrapper, leaving the timeout to mako's defaults."""
    _notify(title, body, urgency=urgency, tag=tag or None, expire_time=None)


# ─────────────────────────────────────────────
#  Microphone
# ─────────────────────────────────────────────


def get_mic_status():
    """Return True if mic is muted"""
    try:
        return _wpctl_volume(SOURCE)[1]
    except subprocess.CalledProcessError:
        return True


def send_mic_notification(is_muted: bool):
    if is_muted:
        notify("Microphone", "󰍭 Microphone Muted", urgency="normal", tag="microphone")
    else:
        notify("Microphone", "󰍬 Microphone Live", urgency="critical", tag="microphone")


@lazy.function
def toggle_mute_audio_input(_qtile):
    """Toggle microphone mute"""

    def _do():
        try:
            subprocess.run(["wpctl", "set-mute", SOURCE, "toggle"], check=True)
            send_mic_notification(get_mic_status())
        except subprocess.CalledProcessError:
            notify("Microphone Error", "Could not toggle mic", urgency="critical")

    threading.Thread(target=_do, daemon=True).start()


# ─────────────────────────────────────────────
#  Output
# ─────────────────────────────────────────────


def get_audio_output_device():
    sink = subprocess.run(
        ["pactl", "get-default-sink"], capture_output=True, text=True
    ).stdout.strip()

    sinks_out = subprocess.run(
        ["pactl", "list", "sinks"], capture_output=True, text=True
    ).stdout

    match = re.search(rf"(?s)Name: {re.escape(sink)}\n(.*?)(?=\nName:|\Z)", sinks_out)
    if not match:
        return "N/A"

    block = match.group(1)
    port_match = re.search(r"Active Port:\s*(\S+)", block)
    if not port_match:
        return "N/A"

    port = port_match.group(1)
    return port.replace("analog-output-", "").replace("-", " ").title()


# ─────────────────────────────────────────────
#  Volume (Output Audio)
# ─────────────────────────────────────────────


def _wpctl_volume(node):
    """Return (volume %, is_muted) for a wpctl node, e.g. "Volume: 0.80 [MUTED]"."""
    out = subprocess.run(
        ["wpctl", "get-volume", node], capture_output=True, text=True, check=True
    ).stdout
    match = re.search(r"Volume:\s*([\d.]+)", out)
    volume = round(float(match.group(1)) * 100) if match else 0
    return volume, "[MUTED]" in out


def get_volume():
    """Return (volume %, is_muted)"""
    try:
        return _wpctl_volume(SINK)
    except subprocess.CalledProcessError:
        return 0, False


def send_volume_notification(volume: int, is_muted: bool):
    # mako colours the border/title to match (~/.config/mako/config)
    green, red, gold, grey = (
        Colours.BRIGHT_GREEN,
        Colours.WARNING,
        Colours.GOLD,
        Colours.GREY,
    )
    bar_len = 35
    if is_muted:
        icon = "󰝟"
        message = f"Volume Muted ({volume}%)"
        colour = gold
        bar = f'<span color="{gold}">' + "░" * bar_len + "</span>"
    else:
        icon = "󰕿" if volume == 0 else "󰖀" if volume < 50 else "󰕾"
        message = f"Volume: {volume}%"
        colour = red if volume > 100 else green

        clamped = min(volume, MAX_VOLUME)
        safe_blocks = int(bar_len * (100 / MAX_VOLUME))
        filled = int((clamped / MAX_VOLUME) * bar_len)
        safe_filled = min(filled, safe_blocks)
        danger_filled = max(0, filled - safe_blocks)
        empty = bar_len - safe_filled - danger_filled

        bar = (
            f'<span color="{green}">' + "█" * safe_filled + "</span>"
            f'<span color="{red}">' + "█" * danger_filled + "</span>"
            f'<span color="{grey}">' + "░" * empty + "</span>"
        )

    urgency = "critical" if volume > 100 else "normal" if is_muted else "low"
    notify(
        "Volume",
        f'<span color="{colour}"><b>{icon} {message}</b></span>\n{bar}',
        urgency=urgency,
        tag="volume",
    )


# ─────────────────────────────────────────────
#  Qtile Bindings
# ─────────────────────────────────────────────


def _change_volume(*wpctl_args):
    """Run a wpctl command on the default sink, then show the new volume."""

    def _do():
        subprocess.run(["wpctl", *wpctl_args])
        send_volume_notification(*get_volume())

    threading.Thread(target=_do, daemon=True).start()


@lazy.function
def raise_volume(_qtile):
    # -l caps the volume at MAX_VOLUME
    _change_volume("set-volume", "-l", str(MAX_VOLUME / 100), SINK, "5%+")


@lazy.function
def lower_volume(_qtile):
    _change_volume("set-volume", SINK, "5%-")


@lazy.function
def toggle_mute_audio_output(_qtile):
    _change_volume("set-mute", SINK, "toggle")
