import subprocess
import os
import re
from datetime import datetime

from libqtile.lazy import lazy


@lazy.function
def cycle_keyboard_layout(_qtile):
    import subprocess
    import os

    layouts = ["us", "zh", "de"]
    state_file = "/tmp/qtile_kb_layout_state"

    # Read current state
    current_index = 0
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            current_index = int(f.read().strip())

    # Cycle to next
    next_index = (current_index + 1) % len(layouts)
    next_layout = layouts[next_index]

    # Set layout
    subprocess.Popen(["localectl", "set-x11-keymap", next_layout])

    # Save state
    with open(state_file, "w") as f:
        f.write(str(next_index))

    # Show current layout
    subprocess.run(["notify-send", f"Layout: {next_layout.upper()}"])


def get_audio_output_device():
    sink = subprocess.run(
        ["pactl", "get-default-sink"], capture_output=True, text=True
    ).stdout.strip()

    sinks_out = subprocess.run(
        ["pactl", "list", "sinks"], capture_output=True, text=True
    ).stdout

    # Isolate the block for the current sink
    match = re.search(rf"(?s)Name: {re.escape(sink)}\n(.*?)(?=\nName:|\Z)", sinks_out)
    if not match:
        return "Audio: Unknown"

    block = match.group(1)

    port_match = re.search(r"Active Port:\s*(\S+)", block)
    if not port_match:
        return "Audio: Unknown"

    port = port_match.group(1)
    pretty = port.replace("analog-output-", "").replace("-", " ").title()

    return pretty


def shift_group(qtile, direction):
    groups = qtile.groups
    current_group = qtile.current_group
    idx = [group.name for group in groups].index(current_group.name)
    new_idx = (idx + direction) % len(groups)
    qtile.current_window.togroup(groups[new_idx].name)
    if direction == 1:
        lazy.screen.next_group()
    else:
        lazy.screen.prev_group()


def get_audio_input_device():
    """Return the current default audio input (microphone) using pactl."""
    try:
        result = subprocess.run(
            ["pactl", "get-default-source"],
            capture_output=True,
            text=True,
            check=True,
        )
        source = result.stdout.strip()

        # Get human-readable description
        desc = subprocess.run(
            ["pactl", "list", "sources"],
            capture_output=True,
            text=True,
        ).stdout

        for block in desc.split("Source #"):
            if source in block:
                for line in block.splitlines():
                    if "Description:" in line:
                        return line.split("Description:")[1].strip()

        return source  # fallback
    except Exception:
        return "No Mic"


def notify(title: str, message: str):
    subprocess.run(["notify-send", title, message], check=False)


def timestamp_file(prefix: str, ext: str, folder) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{folder}/{prefix}_{ts}.{ext}"


def take_screenshot(_qtile):
    IMAGE_DIR = os.path.expanduser("~/Pictures/Screenshots")
    os.makedirs(IMAGE_DIR, exist_ok=True)
    out = timestamp_file("screenshot", "png", IMAGE_DIR)

    subprocess.Popen(["grim", out])

    notify("Screenshot Taken", out)
