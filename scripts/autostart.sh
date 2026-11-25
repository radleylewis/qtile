#!/bin/sh

# Send this script's and its daemons' output to a log (fresh each login) instead of
# the terminal, where it would be printed over the login screen.
LOG="${XDG_STATE_HOME:-$HOME/.local/state}/qtile-autostart.log"
mkdir -p "$(dirname "$LOG")"
exec >"$LOG" 2>&1

# Desktop name for xdg-desktop-portal: "wlroots" makes it use the wlr backend for
# screen sharing/screenshots (see ~/.config/xdg-desktop-portal/portals.conf).
export XDG_CURRENT_DESKTOP=qtile:wlroots
# Services that D-Bus starts on demand (portals, ...) only see the bus's environment,
# which was created before qtile set the display variables: pass them on.
dbus-update-activation-environment DISPLAY WAYLAND_DISPLAY XDG_SESSION_TYPE XDG_CURRENT_DESKTOP

# screens: managed by kanshi
kanshi &

# Wallpapers per monitor
swaybg -m fill -i "$XDG_CONFIG_HOME/qtile/assets/wallpapers/background.jpg" &

# Start notification daemon
mako &

# audio
pipewire &
sleep 1
pipewire-pulse &
wireplumber &

# clipboard history (Super + v)
if command -v cliphist >/dev/null; then
	wl-paste --watch cliphist store &
fi

# gestures
libinput-gestures-setup start

# night light (times/temperatures in ~/.config/gammastep/config.ini)
gammastep &

# desktop portals (screen sharing, file dialogs): they live in /usr/lib, not on PATH
/usr/lib/xdg-desktop-portal-wlr &
sleep 1
/usr/lib/xdg-desktop-portal &

# idle/lock
dim_timeout=120  # 2 minutes to dim
lock_timeout=300 # 5 minutes to lock
BRIGHTNESS_FILE="/tmp/prev_brightness"
DIM_VALUE=10

swayidle -w \
	timeout $dim_timeout "current=\$(brightnessctl g); max=\$(brightnessctl m); percent=\$((current * 100 / max)); if [ \$percent -gt $DIM_VALUE ]; then brightnessctl g > $BRIGHTNESS_FILE && brightnessctl set ${DIM_VALUE}%; fi" \
	resume "[ -f $BRIGHTNESS_FILE ] && brightnessctl set \$(cat $BRIGHTNESS_FILE)" \
	timeout $lock_timeout "$HOME/.config/qtile/scripts/sleep.sh" \
	resume "[ -f $BRIGHTNESS_FILE ] && brightnessctl set \$(cat $BRIGHTNESS_FILE)" &
