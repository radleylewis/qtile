import subprocess
import os
import re
from datetime import datetime
from typing import Optional

from libqtile.lazy import lazy


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


def notify(
    title: str,
    message: str,
    replace_id: Optional[int] = None,
    app_name: Optional[str] = "",
    expire_time: int = 1_200,
    urgency: str = "normal",
):
    cmd = ["notify-send"]
    if replace_id:
        cmd.append(f"--replace-id={replace_id}")
    if app_name:
        cmd.append(f"--app-name={app_name}")

    cmd.append(f"--urgency={urgency}")
    cmd.append(f"--expire-time={expire_time}")

    subprocess.run(cmd + [title, message], check=False)


def timestamp_file(prefix: str, ext: str, folder) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{folder}/{prefix}_{ts}.{ext}"


def take_screenshot(_qtile):
    IMAGE_DIR = os.path.expanduser("~/Pictures/Screenshots")
    os.makedirs(IMAGE_DIR, exist_ok=True)
    out = timestamp_file("screenshot", "png", IMAGE_DIR)

    subprocess.Popen(["grim", out])

    notify("Screenshot Taken", out)
