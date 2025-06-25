import subprocess
import re

from libqtile.lazy import lazy


def send_notification(title, message, urgency="normal", icon=None):
    cmd = ["dunstify", title, message, "-u", urgency]
    if icon:
        cmd.extend(["-i", icon])

    subprocess.run(cmd, check=False)


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
