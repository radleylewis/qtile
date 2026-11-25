#!/bin/sh

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

# desktop backend
xdg-desktop-portal-wlr &
sleep 1
xdg-desktop-portal &

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
