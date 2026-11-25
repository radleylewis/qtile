#!/bin/sh
# Set up a fresh Artix (OpenRC) install for this desktop: packages, the system files
# that live outside $HOME, services and the GTK theme. Dotfiles themselves come from
# the dotfiles repo; this covers everything they can't.
#
# Usage: sh ~/.config/qtile/scripts/bootstrap.sh           (dry run: print the steps)
#        sh ~/.config/qtile/scripts/bootstrap.sh --apply   (do it; asks for sudo)
# Safe to re-run: every step is idempotent.

APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1

run() {
	echo "+ $*"
	[ "$APPLY" -eq 1 ] || return 0
	"$@" || {
		echo "FAILED: $*" >&2
		exit 1
	}
}

# write_root FILE CONTENT: create a root-owned config file (only if it differs)
write_root() {
	if [ -f "$1" ] && [ "$(cat "$1")" = "$2" ]; then
		echo "= $1 already up to date"
		return
	fi
	echo "+ write $1:"
	printf '%s\n' "$2" | sed 's/^/    /'
	[ "$APPLY" -eq 1 ] || return 0
	sudo mkdir -p "$(dirname "$1")" && printf '%s\n' "$2" | sudo tee "$1" >/dev/null
}

echo "== packages (official repos)"
run sudo pacman -S --needed \
	qtile xorg-xwayland python-psutil python-dbus-fast \
	alacritty rofi rofi-calc rofi-emoji cliphist wtype wl-clipboard \
	mako libnotify brightnessctl playerctl grim slurp wev \
	pipewire pipewire-pulse wireplumber \
	kanshi swayidle swaylock swaybg gammastep \
	xdg-desktop-portal xdg-desktop-portal-wlr xdg-desktop-portal-gtk \
	bluez bluez-utils \
	ttf-jetbrains-mono-nerd papirus-icon-theme

echo "== packages (AUR)"
if command -v paru >/dev/null; then
	run paru -S --needed libinput-gestures bluetuith
else
	echo "! paru not found: install libinput-gestures and bluetuith from the AUR manually"
fi

echo "== system files"
# S3 resume is broken on this Libreboot T480; suspend must use s2idle (see README)
write_root /etc/elogind/sleep.conf.d/20-s2idle.conf "[Sleep]
SuspendState=freeze"

# Login session (pick "Qtile (Wayland, D-Bus)" in ly): gives qtile and everything it starts one
# session bus. Plain "qtile start" has none, so apps end up on separate buses.
write_root /usr/share/wayland-sessions/qtile-dbus.desktop "[Desktop Entry]
Name=Qtile (Wayland, D-Bus)
Comment=Qtile on Wayland with its own D-Bus session bus
Exec=dbus-run-session qtile start -b wayland
Type=Application
Keywords=wm;tiling"

echo "== services and groups"
run sudo rc-update add bluetoothd default
# libinput-gestures reads touchpad events directly
id -nG | grep -qw input || run sudo gpasswd -a "$USER" input

echo "== GTK theme (dark Adwaita, Papirus icons, Adwaita cursor)"
run gsettings set org.gnome.desktop.interface color-scheme prefer-dark
run gsettings set org.gnome.desktop.interface gtk-theme Adwaita-dark
run gsettings set org.gnome.desktop.interface icon-theme Papirus-Dark
run gsettings set org.gnome.desktop.interface cursor-theme Adwaita
run gsettings set org.gnome.desktop.interface cursor-size 24

if [ "$APPLY" -eq 1 ]; then
	echo "done. Log out and back in (group changes and qtile's cursor need a fresh session)."
else
	echo "dry run only: re-run with --apply to make these changes"
fi
