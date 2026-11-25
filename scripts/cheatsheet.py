#!/usr/bin/env python
"""Print a Markdown cheatsheet of the qtile keybindings, generated from config.py.

Usage: python ~/.config/qtile/scripts/cheatsheet.py > cheatsheet.md
       python ~/.config/qtile/scripts/cheatsheet.py --plain   (one line per binding, for rofi)
"""

import os
import sys

# Run from the qtile config dir, so `import config` and its packages resolve
QTILE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[0] = QTILE_DIR
os.chdir(QTILE_DIR)

import config  # noqa: E402

MODIFIERS = {"mod4": "Super", "mod1": "Alt", "control": "Ctrl", "shift": "Shift"}
KEYS = {"equal": "=", "minus": "-", "space": "Space", "period": ".", "slash": "/"}


def shortcut(modifiers, key):
    parts = [MODIFIERS.get(m, m) for m in modifiers] + [KEYS.get(key, key)]
    return " + ".join(parts)


def key_rows():
    """(shortcut, description) rows; consecutive keys sharing a description merge,
    e.g. "Super + Alt + Left / h"."""
    rows = []
    previous = None
    for k in config.keys:
        group = (tuple(k.modifiers), k.desc)
        if group == previous:
            label, desc = rows[-1]
            rows[-1] = (f"{label} / {KEYS.get(k.key, k.key)}", desc)
        else:
            rows.append((shortcut(k.modifiers, k.key), k.desc or "-"))
        previous = group
    return rows


def mouse_rows():
    # Mouse bindings have no desc, so describe them by their command name.
    rows = []
    for m in config.mouse:
        action = m.commands[0].name.replace("_", " ").capitalize()
        rows.append((shortcut(m.modifiers, m.button), action))
    return rows


def table(title, rows):
    lines = [f"## {title}", "", "| Shortcut | Action |", "|----------|--------|"]
    lines += [f"| `{s}` | {d} |" for s, d in rows]
    return "\n".join(lines)


if __name__ == "__main__":
    if "--plain" in sys.argv:
        rows = key_rows() + mouse_rows()
        width = max(len(s) for s, _ in rows)
        for s, d in rows:
            print(f"{s:<{width}}   {d}")
        sys.exit()

    print("# Qtile Keybindings\n")
    print(table("Keyboard", key_rows()))
    print()
    print(table("Mouse", mouse_rows()))
