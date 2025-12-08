#!/bin/sh

# screens: managed by kanshi
kanshi &

# Wallpapers per monitor
swaybg -m fill -i "$HOME/Pictures/background.jpeg" &

# Start notification daemon
mako &

# Start gestures
libinput-gestures-setup start &

# Timings
dim_timeout=120  # 1 minute of inactivity to dim
lock_timeout=300 # 5 minutes of inactivity to lock

# Screen
BRIGHTNESS_FILE="/tmp/prev_brightness"
swayidle -w \
	timeout $dim_timeout "brightnessctl g > $BRIGHTNESS_FILE && brightnessctl set 10" \
	resume "[ -f $BRIGHTNESS_FILE ] && brightnessctl set \$(cat $BRIGHTNESS_FILE)" \
	timeout $lock_timeout "$HOME/.config/qtile/scripts/sleep.sh" \
	resume "[ -f $BRIGHTNESS_FILE ] && brightnessctl set\$(cat $BRIGHTNESS_FILE)" &
