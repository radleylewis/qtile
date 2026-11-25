#!/bin/sh

if pactl list sink-inputs | grep -q 'state: RUNNING'; then
	exit 0
else
	pgrep -x swaylock >/dev/null || swaylock -f -i ~/.config/qtile/assets/wallpapers/lock_screen.jpg
	sleep 60
	# Only suspend if the screen is still locked (user hasn't come back).
	# Needs s2idle: S3 resume is broken on Libreboot 26.01 T480 (black/frozen screen), so
	# /etc/elogind/sleep.conf.d/20-s2idle.conf sets SuspendState=freeze (tested 2026-11-25).
	pgrep -x swaylock >/dev/null && loginctl suspend
fi
