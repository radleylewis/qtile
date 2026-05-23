#!/bin/sh

if pactl list sink-inputs | grep -q 'state: RUNNING'; then
	exit 0 # Audio is playing — do not lock
else
	swaylock -i ~/.config/qtile/assets/wallpapers/lock_screen.jpg &
	sleep 2
	loginctl suspend
fi
