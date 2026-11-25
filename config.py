import os
import subprocess
from libqtile import hook, qtile
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.layout.floating import Floating
from libqtile.layout.max import Max
from libqtile.layout.xmonad import MonadTall
from libqtile.lazy import lazy
from assets.constants import Colours, FONT_TYPE
from utils.audio import (
    raise_volume,
    toggle_mute_audio_output,
    lower_volume,
    toggle_mute_audio_input,
)
from utils.brightness import decrease_brightness, increase_brightness
from top_bar import make_top_bar
from scripts.helpers import shift_group, take_screenshot

terminal = "alacritty"
meta = "mod4"
alt = "mod1"

XDG_CONFIG_DIR = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))


@hook.subscribe.startup_once
def on_startup():
    autostart = os.path.expanduser(f"{XDG_CONFIG_DIR}/qtile/scripts/autostart.sh")
    subprocess.Popen([autostart])


# qtile draws its bars above the session-lock surface, so hide them while locked.
# Only hide/unhide the bar's window: Bar.show() re-lays out the group, which refocuses
# the app window and steals keyboard input from the lock screen (can't unlock).
def _show_bars(show):
    for screen in qtile.screens:
        if screen.top and screen.top.window:
            if show:
                screen.top.window.unhide()
            else:
                screen.top.window.hide()


@hook.subscribe.locked
def hide_bars_when_locked():
    _show_bars(False)


@hook.subscribe.unlocked
def show_bars_when_unlocked():
    _show_bars(True)


# Bluetooth Manager
@hook.subscribe.client_new
def center_bluetuith(client):
    wm_class = client.get_wm_class()
    if wm_class and any("bluetuith" in c for c in wm_class):
        screen = client.qtile.current_screen
        sw = screen.width
        sh = screen.height
        w = 800
        h = 400
        client.set_size_floating(w, h)
        # positions are absolute, so offset by the screen's origin
        client.set_position_floating(screen.x + (sw - w) // 2, screen.y + (sh - h) // 2)


keys = [
    # ROFI SCRIPTS
    Key(
        [meta],
        "space",
        lazy.spawn('rofi -show combi -modes combi -combi-modes "window,drun"'),
        desc="App launcher (apps + open windows)",
    ),
    Key(
        [meta],
        "c",
        lazy.spawn("rofi -show calc -modi calc -no-show-match -no-sort"),
        desc="Calculator",
    ),
    Key(
        [meta, "shift"],
        "f",
        lazy.spawn("rofi -show filebrowser -show-hidden"),
        desc="File browser",
    ),
    Key([meta, "shift"], "r", lazy.spawn("rofi -show run"), desc="Run command"),
    Key([meta], "w", lazy.spawn("rofi -show window"), desc="Window switcher"),
    Key(
        [meta],
        "v",
        lazy.spawn(
            "cliphist list | rofi -dmenu -i -p Clipboard -display-columns 2"
            " | cliphist decode | wl-copy",
            shell=True,
        ),
        desc="Clipboard history",
    ),
    Key(
        [meta],
        "period",
        lazy.spawn("rofi -modi emoji -show emoji"),
        desc="Emoji picker",
    ),
    Key(
        [meta],
        "slash",
        lazy.spawn(
            f"python3 {XDG_CONFIG_DIR}/qtile/scripts/cheatsheet.py --plain"
            " | rofi -dmenu -i -p Keys -theme-str 'window {width: 900px;}'",
            shell=True,
        ),
        desc="Keybinding cheatsheet",
    ),
    Key(
        [meta],
        "Escape",
        lazy.spawn(f"{XDG_CONFIG_DIR}/rofi/scripts/power-manager"),
        desc="Power menu",
    ),
    Key(
        [meta],
        "p",
        lazy.spawn(
            f"rofi -show performance-profile -theme {XDG_CONFIG_DIR}/rofi/performance-profile.rasi"
        ),
        desc="Performance profile menu",
    ),
    Key(
        [meta],
        "a",
        lazy.spawn(
            f"rofi -show audio-output -theme {XDG_CONFIG_DIR}/rofi/microphone.rasi"
        ),
        desc="Audio output menu",
    ),
    Key(
        [meta],
        "i",
        lazy.spawn(
            f"rofi -show microphone -theme {XDG_CONFIG_DIR}/rofi/microphone.rasi"
        ),
        desc="Audio input menu",
    ),
    Key(
        [meta],
        "n",
        lazy.spawn(f"{XDG_CONFIG_DIR}/rofi/scripts/wifi-manager"),
        desc="WiFi menu",
    ),
    Key(
        [meta],
        "b",
        lazy.spawn(f"{terminal} --class bluetuith -e bluetuith"),
        desc="Bluetooth manager",
    ),
    Key(
        [meta],
        "r",
        lazy.spawn(f"rofi -show av-recorder -theme {XDG_CONFIG_DIR}/rofi/common.rasi"),
        desc="Screen/mic recorder menu",
    ),
    Key([], "Print", lazy.function(take_screenshot), desc="Screenshot"),
    Key([meta, alt], "Left", lazy.screen.prev_group(), desc="Move to previous group"),
    Key([meta, alt], "h", lazy.screen.prev_group(), desc="Move to previous group"),
    Key([meta, alt], "Right", lazy.screen.next_group(), desc="Move to next group"),
    Key([meta, alt], "l", lazy.screen.next_group(), desc="Move to next group"),
    Key(
        [meta, alt, "shift"],
        "h",
        lazy.function(lambda q: shift_group(q, -1)),
        lazy.screen.prev_group(),
        desc="Move window to previous group",
    ),
    Key(
        [meta, alt, "shift"],
        "Left",
        lazy.function(lambda q: shift_group(q, -1)),
        lazy.screen.prev_group(),
        desc="Move window to previous group",
    ),
    Key(
        [meta, alt, "shift"],
        "l",
        lazy.function(lambda q: shift_group(q, 1)),
        lazy.screen.next_group(),
        desc="Move window to next group",
    ),
    Key(
        [meta, alt, "shift"],
        "Right",
        lazy.function(lambda q: shift_group(q, 1)),
        lazy.screen.next_group(),
        desc="Move window to next group",
    ),
    Key([meta], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([meta], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([meta], "j", lazy.layout.down(), desc="Move focus down"),
    Key([meta], "k", lazy.layout.up(), desc="Move focus up"),
    Key(
        [meta, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"
    ),
    Key(
        [meta, "shift"],
        "l",
        lazy.layout.shuffle_right(),
        desc="Move window to the right",
    ),
    Key([meta, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([meta, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    Key([meta], "equal", lazy.layout.grow(), desc="Grow window"),
    Key([meta], "minus", lazy.layout.shrink(), desc="Shrink window"),
    Key([meta], "u", lazy.layout.reset(), desc="Reset window size"),
    Key([meta, "shift"], "n", lazy.layout.normalize(), desc="Normalise layout"),
    Key([meta], "o", lazy.layout.maximize(), desc="Maximise window"),
    Key([meta], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key([meta], "d", lazy.next_layout(), desc="Toggle between layouts"),
    Key([meta], "q", lazy.window.kill(), desc="Kill focused window"),
    Key(
        [meta],
        "z",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on focused window",
    ),
    Key(
        [meta],
        "f",
        lazy.window.toggle_floating(),
        desc="Toggle floating on focused window",
    ),
    Key([meta], "Tab", lazy.group.next_window(), desc="Cycle through windows"),
    Key(
        [meta, "shift"],
        "Tab",
        lazy.group.prev_window(),
        desc="Cycle backwards through windows",
    ),
    Key([meta, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    # Key([], "XF86Keyboard", cycle_keyboard_layout),
    Key([], "XF86Favorites", lazy.spawn("brave"), desc="Brave browser"),
    Key([], "XF86Go", lazy.spawn("rfkill unblock bluetooth"), desc="Unblock Bluetooth"),
    Key([], "Cancel", lazy.spawn("rfkill block bluetooth"), desc="Block Bluetooth"),
    Key([], "XF86AudioRaiseVolume", raise_volume, desc="Volume up"),
    Key([], "XF86AudioMute", toggle_mute_audio_output, desc="Toggle mute"),
    Key([], "XF86AudioLowerVolume", lower_volume, desc="Volume down"),
    Key([], "XF86MonBrightnessDown", decrease_brightness, desc="Brightness down"),
    Key([], "XF86MonBrightnessUp", increase_brightness, desc="Brightness up"),
    Key([], "XF86AudioMicMute", toggle_mute_audio_input, desc="Toggle mic mute"),
    # notifications (mako)
    Key([meta], "x", lazy.spawn("makoctl dismiss"), desc="Dismiss notification"),
    Key([meta, "shift"], "x", lazy.spawn("makoctl dismiss -a"), desc="Dismiss all notifications"),
    Key([meta], "grave", lazy.spawn("makoctl restore"), desc="Restore last dismissed notification"),
]

groups = [Group(str(i)) for i in range(1, 6)]  # main screen groups

for g in groups:  # exclude laptop group
    keys.extend(
        [
            Key([meta], g.name, lazy.group[g.name].toscreen(), desc=f"Switch to group {g.name}"),
            Key(
                [meta, "shift"],
                g.name,
                lazy.window.togroup(g.name),
                desc=f"Move window to group {g.name}",
            ),
        ]
    )

# Add key bindings to switch VTs in Wayland.
# We can't check qtile.core.name in default config as it is loaded before qtile is started
# We therefore defer the check until the key binding is run by using .when(func=...)
for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )

config = {
    "margin": 10,
    "single_margin": 10,
    "border_focus": Colours.BRIGHT_GREEN,
    "border_normal": Colours.GREY,
}

layouts = [
    MonadTall(**config),
    Max(**config),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

widget_defaults = dict(
    font=FONT_TYPE,
    fontsize=13,
    padding=3,
)

extension_defaults = widget_defaults.copy()


# Build one Screen (with its own bar) per connected output; qtile calls this
# again whenever outputs change (reconfigure_screens, below; layout via kanshi).
#
# Reuse the bar of a monitor that's still connected: qtile keeps that monitor's old
# Screen (matched by output) and never finalizes its bar, so a fresh bar would leave
# the old one drawn on top. Workaround for qtile 0.37.1: fixed upstream by
# https://github.com/qtile/qtile/pull/6055 — remove this once qtile includes it.
def generate_screens(outputs):
    def bar_for(output):
        for screen in qtile.screens:
            if getattr(screen, "output", None) == output and screen.top:
                return screen.top
        return make_top_bar()

    return [Screen(top=bar_for(output)) for output in outputs]


# Drag floating layouts.
mouse = [
    Drag(
        [meta],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [meta], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()
    ),
    Click([meta], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = Floating(
    float_rules=[
        Match(wm_class="bluetuith"),
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ],
    border_focus=Colours.HIGHLIGHT,
    border_normal=Colours.GOLD,
    border_width=2,
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = {
    "type:touchpad": {
        "tap": True,
        "natural_scroll": True,
        "dwt": True,  # disable while typing
    },
}

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
