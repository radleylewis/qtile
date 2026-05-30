#!/bin/sh

if pactl list sink-inputs | grep -q 'state: RUNNING'; then
	exit 0
else
	swaylock -i ~/.config/qtile/assets/wallpapers/lock_screen.jpg &
	sleep 2
	echo "$(date): calling zzz" >>/tmp/sleep.log
	sudo zzz
	echo "$(date): resumed from zzz" >>/tmp/sleep.log
fi
