#!/bin/sh

if pactl list sink-inputs | grep -q 'state: RUNNING'; then
	exit 0
else
	swaylock -i ~/.config/qtile/assets/wallpapers/lock_screen.jpg &
	sleep 60
	sudo zzz
fi
