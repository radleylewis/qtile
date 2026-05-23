#!/bin/sh

# screens: managed by kanshi
kanshi &

# Wallpapers per monitor
swaybg -m fill -i "$XDG_CONFIG_HOME/qtile/assets/wallpapers/background.jpg" &

# Start notification daemon
mako &

# audio
pipewire &
pipewire-pulse &
wireplumber &

# Start gestures
libinput-gestures-setup start &

# Start auto-cpufreq
if ! pgrep -x auto-cpufreq >/dev/null; then
    auto-cpufreq --daemon &
fi

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
