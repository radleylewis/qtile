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

# Start auto-cpufreq
if ! pgrep -x auto-cpufreq >/dev/null; then
	auto-cpufreq --daemon &
fi

# gestures
libinput-gestures-setup start

# desktop backend
xdg-desktop-portal &

# idle/lock
dim_timeout=120  # 2 minutes to dim
lock_timeout=300 # 5 minutes to lock
BRIGHTNESS_FILE="/tmp/prev_brightness"
swayidle -w \
	timeout $dim_timeout "brightnessctl g > $BRIGHTNESS_FILE && brightnessctl set 10%" \
	resume "[ -f $BRIGHTNESS_FILE ] && brightnessctl set \$(cat $BRIGHTNESS_FILE)" \
	timeout $lock_timeout "$HOME/.config/qtile/scripts/sleep.sh" \
	resume "[ -f $BRIGHTNESS_FILE ] && brightnessctl set \$(cat $BRIGHTNESS_FILE)" &
resume "[ -f $BRIGHTNESS_FILE ] && brightnessctl set $(cat $BRIGHTNESS_FILE)" &
