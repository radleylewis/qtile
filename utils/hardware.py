"""Detect machine-specific hardware so the bar works on any laptop."""

import glob
import os
from typing import Optional


def _read(path: str) -> Optional[str]:
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError:
        return None


def batteries() -> list[str]:
    """System batteries (e.g. ["BAT0", "BAT1"]), excluding peripherals like mice."""
    names = []
    for path in sorted(glob.glob("/sys/class/power_supply/*")):
        if _read(f"{path}/type") == "Battery" and _read(f"{path}/scope") != "Device":
            names.append(os.path.basename(path))
    return names


def wifi_interface() -> Optional[str]:
    """First wireless network interface (e.g. "wlan0"), or None."""
    found = sorted(glob.glob("/sys/class/net/*/wireless"))
    return os.path.basename(os.path.dirname(found[0])) if found else None


def has_bluetooth() -> bool:
    return bool(glob.glob("/sys/class/bluetooth/hci*"))
