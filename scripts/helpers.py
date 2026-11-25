import subprocess
import os
from datetime import datetime
from typing import Optional


def shift_group(qtile, direction):
    groups = qtile.groups
    current_group = qtile.current_group
    if qtile.current_window is None:
        return
    idx = [group.name for group in groups].index(current_group.name)
    new_idx = (idx + direction) % len(groups)
    qtile.current_window.togroup(groups[new_idx].name)


def notify(
    title: str,
    message: str,
    replace_id: Optional[int] = None,
    app_name: Optional[str] = "",
    expire_time: Optional[int] = 1_200,
    urgency: str = "normal",
    tag: Optional[str] = None,
):
    cmd = ["notify-send"]
    if app_name:
        cmd.append(f"--app-name={app_name}")
    cmd.append(f"--urgency={urgency}")
    if expire_time is not None:
        cmd.append(f"--expire-time={expire_time}")
    if tag:
        cmd += [f"--hint=string:x-canonical-private-synchronous:{tag}"]
    elif replace_id:
        cmd.append(f"--replace-id={replace_id}")
    subprocess.run(cmd + [title, message], check=False)


def timestamp_file(prefix: str, ext: str, folder) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{folder}/{prefix}_{ts}.{ext}"


def take_screenshot(_qtile):
    IMAGE_DIR = os.path.expanduser("~/Pictures/Screenshots")
    os.makedirs(IMAGE_DIR, exist_ok=True)
    out = timestamp_file("screenshot", "png", IMAGE_DIR)

    # Save to file and copy to the clipboard
    subprocess.Popen(
        ["sh", "-c", 'grim "$1" && wl-copy --type image/png < "$1"', "sh", out]
    )

    notify("Screenshot Taken", f"{out}\nCopied to clipboard")
