from libqtile import hook, qtile
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.layout.floating import Floating
from libqtile.layout.max import Max
from libqtile.layout.xmonad import MonadTall
from libqtile.lazy import lazy
from libqtile.log_utils import logger

from assets.constants import Colours, FONT_TYPE 

from scripts.audio import (
    raise_volume,
    toggle_mute_audio_output,
    lower_volume,
    toggle_mute_audio_input,
)
from scripts.menus import (
    autostart,
    bluetooth_menu,
    power_menu,
    performance_menu,
    recorder_menu,
    wifi_menu,
)
from scripts.screen import decrease_brightness, increase_brightness
from scripts.recorder import take_screenshot
from top_bar import top_bar
from scripts.utils import cycle_keyboard_layout, shift_group

terminal = "alacritty"

meta = "mod4"
alt = "mod1"


@hook.subscribe.startup_once
def on_startup():
    autostart()

keys = [
    Key([], "Print", take_screenshot),
    Key([meta, alt], "Left", lazy.screen.prev_group(), desc="Move to previous group"),
    Key([meta, alt], "h", lazy.screen.prev_group(), desc="Move to previous group"),
    Key([meta, alt], "Right", lazy.screen.next_group(), desc="Move to next group"),
    Key([meta, alt], "l", lazy.screen.next_group(), desc="Move to next group"),
    Key(
        [alt, "shift"],
        "h",
        lazy.function(lambda qtile: shift_group(qtile, -1)),
        lazy.screen.prev_group(),
        desc="Move window to previous group",
    ),
    Key(
        [alt, "shift"],
        "Left",
        lazy.function(lambda qtile: shift_group(qtile, -1)),
        lazy.screen.prev_group(),
        desc="Move window to previous group",
    ),
    Key(
        [alt, "shift"],
        "l",
        lazy.function(lambda qtile: shift_group(qtile, 1)),
        lazy.screen.next_group(),
        desc="Move window to next group",
    ),
    Key(
        [alt, "shift"],
        "Right",
        lazy.function(lambda qtile: shift_group(qtile, 1)),
        lazy.screen.next_group(),
        desc="Move window to next group",
    ),
    Key([meta], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([meta], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([meta], "j", lazy.layout.down(), desc="Move focus down"),
    Key([meta], "k", lazy.layout.up(), desc="Move focus up"),
    Key([meta], "Return", lazy.layout.next(), desc="Move window focus to other window"),
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
    Key([meta], "m", lazy.layout.grow()),
    Key([meta], "s", lazy.layout.shrink()),
    Key([meta], "u", lazy.layout.reset()),
    Key([meta, "shift"], "n", lazy.layout.normalize()),
    Key([meta], "o", lazy.layout.maximize()),
    Key([meta], "t", lazy.spawn(terminal), desc="Launch terminal"),
    Key([meta], "d", lazy.next_layout(), desc="Toggle between layouts"),
    Key([meta], "Tab", lazy.next_screen()),
    Key([meta], "q", lazy.window.kill(), desc="Kill focused window"),
    Key([meta], "Escape", power_menu, desc="power menu"),
    Key([meta], "p", performance_menu, desc="performance menu"),
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
        [meta], "Tab", lazy.group.next_window(), desc="Cycle backwards through windows"
    ),
    Key([meta, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([meta], "space", lazy.spawn("rofi -show drun"), desc="Spawn rofi apps"),
    Key([meta], "w", lazy.spawn("rofi -show window"), desc="Spawn rofi"),
    Key([meta], "n", wifi_menu, desc="Spawn rofi WiFi menu"),
    Key([meta], "r", recorder_menu, desc="Spawn rofi recorder menu"),
    Key([meta], "b", bluetooth_menu, desc="Spawn rofi bluetooth menu"),
    Key([], "XF86Keyboard", cycle_keyboard_layout),
    Key([], "XF86Favorites", lazy.spawn("brave")),
    Key([], "XF86Go", lazy.spawn("rfkill unblock bluetooth")),
    Key([], "Cancel", lazy.spawn("rfkill block bluetooth")),
    Key([], "XF86AudioRaiseVolume", raise_volume),
    Key([], "XF86AudioMute", toggle_mute_audio_output),
    Key([], "XF86AudioLowerVolume", lower_volume),
    Key([], "XF86MonBrightnessDown", decrease_brightness),
    Key([], "XF86MonBrightnessUp", increase_brightness),
    Key([], "XF86AudioMicMute", toggle_mute_audio_input),
]

groups = [Group(str(i)) for i in range(1, 6)]  # main screen groups

for g in groups:  # exclude laptop group
    keys.extend([
        Key([meta], g.name, lazy.group[g.name].toscreen()),
        Key([meta, "shift"], g.name, lazy.window.togroup(g.name))
    ])


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
    "border_focus": Colours.ELECTRIC_BLUE,
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

def make_screens():
    return [Screen(top=top_bar)]

screens = make_screens()

# This hook ensures screens are reconfigured when monitors change
@hook.subscribe.screen_change
def on_screen_change(event):
    logger.warning(f"Screen change detected: {event}")
    lazy.restart()

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
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ],
    border_focus=Colours.ELECTRIC_BLUE,
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
wl_input_rules = None

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
