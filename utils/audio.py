import subprocess
import re
from libqtile.lazy import lazy
import threading

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────


def notify(title: str, body: str, urgency: str = "normal", tag: str = ""):
    """Wrapper around notify-send (for mako)"""
    cmd = ["notify-send", "-u", urgency]

    if tag:
        cmd += [f"--hint=string:x-canonical-private-synchronous:{tag}"]

    cmd.extend([title, body])
    subprocess.Popen(cmd)


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
    if is_muted:
        notify("Microphone", "󰍭 Microphone Muted", urgency="normal", tag="microphone")
    else:
        notify("Microphone", "󰍬 Microphone Live", urgency="critical", tag="microphone")


@lazy.function
def toggle_mute_audio_input(_qtile):
    """Toggle microphone mute"""
    try:
        subprocess.run(
            ["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "toggle"], check=True
        )
        send_mic_notification(get_mic_status())
    except subprocess.CalledProcessError:
        notify("Microphone Error", "Could not toggle mic", urgency="critical")


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
            ["pactl", "get-sink-mute", sink],
            capture_output=True,
            text=True,
            check=True,
        )
        volume_match = re.search(r"/\s*(\d+)%", v.stdout)
        volume = int(volume_match.group(1)) if volume_match else 0
        muted = "yes" in m.stdout
        return volume, muted
    except subprocess.CalledProcessError:
        return 0, False


def send_volume_notification(volume: int, is_muted: bool):
    if is_muted:
        icon = "󰝟"
        message = f"Volume Muted ({volume}%)"
        bar = '<span color="#e2c779">' + "░" * 35 + "</span>"
    else:
        icon = "󰕿" if volume == 0 else "󰖀" if volume < 50 else "󰕾"
        message = f"Volume: {volume}%"

        clamped = min(volume, 130)
        bar_len = 35
        safe_blocks = int(bar_len * (100 / 130))
        filled = int((clamped / 130) * bar_len)

        safe_filled = min(filled, safe_blocks)
        danger_filled = max(0, filled - safe_blocks)
        empty = bar_len - safe_filled - danger_filled

        bar = (
            '<span color="#7ee787">'
            + "█" * safe_filled
            + "</span>"
            + '<span color="#ff6b8a">'
            + "█" * danger_filled
            + "</span>"
            + '<span color="#e2c779">'
            + "░" * empty
            + "</span>"
        )

    urgency = "critical" if volume > 100 else "normal" if is_muted else "low"
    notify(
        "Volume",
        f'<span color="#e2c779">{icon} {message}</span>\n{bar}',
        urgency=urgency,
        tag="volume",
    )


# ─────────────────────────────────────────────
#  Qtile Bindings
# ─────────────────────────────────────────────


@lazy.function
def raise_volume(_qtile):
    def _do():
        sink = get_default_sink()
        if not sink:
            return
        volume, _ = get_volume()
        if volume >= 130:
            return
        subprocess.run(["pactl", "set-sink-volume", sink, "+5%"])
        volume, muted = get_volume()
        if volume > 130:
            subprocess.run(["pactl", "set-sink-volume", sink, "130%"])
            volume = 130
            muted = False
        send_volume_notification(volume, muted)

    threading.Thread(target=_do, daemon=True).start()


@lazy.function
def lower_volume(_qtile):
    def _do():
        sink = get_default_sink()
        if not sink:
            return
        subprocess.run(["pactl", "set-sink-volume", sink, "-5%"])
        volume, muted = get_volume()
        send_volume_notification(volume, muted)

    threading.Thread(target=_do, daemon=True).start()


@lazy.function
def toggle_mute_audio_output(_qtile):
    def _do():
        sink = get_default_sink()
        if not sink:
            return
        subprocess.run(["pactl", "set-sink-mute", sink, "toggle"])
        volume, muted = get_volume()
        send_volume_notification(volume, muted)

    threading.Thread(target=_do, daemon=True).start()
