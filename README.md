# Qtile Configuration

A Qtile Wayland desktop configuration for Artix Linux with OpenRC.

*Author: Radley E. Sidwell-Lewis*

## Dependencies

**Window manager and Wayland:**

```bash
sudo pacman -S qtile python-pywlroots python-pywayland python-xkbcommon xorg-xwayland
```

**Launcher and utilities:**

```bash
sudo pacman -S rofi rofi-calc mako brightnessctl playerctl grim slurp wl-clipboard
```

**Audio:**

```bash
sudo pacman -S pipewire pipewire-pulse wireplumber
```

**Display and idle:**

```bash
sudo pacman -S kanshi swayidle swaylock swaybg
```

**Bluetooth:**

```bash
paru -S bluetuith
```

**Fonts:**

```bash
sudo pacman -S ttf-firacode-nerd
```

**Python dependencies:**

```bash
sudo pacman -S python-psutil
```

---

## Keybindings

### Rofi / Launchers

| Shortcut | Action |
|----------|--------|
| `Super + Space` | Apps / window switcher (combi) |
| `Super + w` | Window switcher |
| `Super + c` | Calculator |
| `Super + Shift + f` | File browser |
| `Super + Shift + r` | Run command |
| `Super + Escape` | Power menu |
| `Super + p` | Performance profile |
| `Super + a` | Audio output |
| `Super + i` | Microphone input |
| `Super + n` | WiFi manager |
| `Super + b` | Bluetooth manager |
| `Super + r` | Screen / mic recorder |

### Applications

| Shortcut | Action |
|----------|--------|
| `Super + Return` | Terminal (alacritty) |
| `Print` | Screenshot |
| `XF86Favorites` | Brave browser |

### Navigation

| Shortcut | Action |
|----------|--------|
| `Super + h` | Focus left |
| `Super + l` | Focus right |
| `Super + j` | Focus down |
| `Super + k` | Focus up |
| `Super + Tab` | Cycle windows forward |
| `Super + Shift + Tab` | Cycle windows backward |

### Window Management

| Shortcut | Action |
|----------|--------|
| `Super + Shift + h` | Move window left |
| `Super + Shift + l` | Move window right |
| `Super + Shift + j` | Move window down |
| `Super + Shift + k` | Move window up |
| `Super + =` | Grow window |
| `Super + -` | Shrink window |
| `Super + u` | Reset window size |
| `Super + Shift + n` | Normalise layout |
| `Super + o` | Maximise window |
| `Super + q` | Kill window |
| `Super + f` | Toggle floating |
| `Super + z` | Toggle fullscreen |
| `Super + d` | Toggle layout |

### Groups / Workspaces

| Shortcut | Action |
|----------|--------|
| `Super + 1-5` | Switch to group |
| `Super + Shift + 1-5` | Move window to group |
| `Super + Alt + Left / h` | Previous group |
| `Super + Alt + Right / l` | Next group |
| `Alt + Shift + Left / h` | Move window to previous group |
| `Alt + Shift + Right / l` | Move window to next group |

### Media Keys

| Shortcut | Action |
|----------|--------|
| `XF86AudioRaiseVolume` | Volume up |
| `XF86AudioLowerVolume` | Volume down |
| `XF86AudioMute` | Toggle mute |
| `XF86AudioMicMute` | Toggle mic mute |
| `XF86MonBrightnessUp` | Brightness up |
| `XF86MonBrightnessDown` | Brightness down |
| `XF86Go` | Unblock Bluetooth |
| `Cancel` | Block Bluetooth |

### System

| Shortcut | Action |
|----------|--------|
| `Super + Ctrl + r` | Reload config |
| `Ctrl + Alt + F1-F7` | Switch VT |

### Mouse

| Shortcut | Action |
|----------|--------|
| `Super + Left click drag` | Move floating window |
| `Super + Right click drag` | Resize floating window |
| `Super + Middle click` | Bring window to front |
