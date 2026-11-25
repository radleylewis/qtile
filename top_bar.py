from libqtile import bar, widget

from assets.constants import Colours, FONT_TYPE, GRAPHICS_DIR
from utils.audio import get_audio_output_device
from utils.hardware import batteries, has_bluetooth, wifi_interface


def _divider():
    return widget.Image(
        filename=f"{GRAPHICS_DIR}/bar_divider_5.svg",
        background=Colours.BACKGROUND,
    )


def _wifi_widgets():
    interface = wifi_interface()
    if interface is None:
        return []
    return [
        widget.Image(
            filename=f"{GRAPHICS_DIR}/internet.png",
            background=Colours.BACKGROUND,
            margin_y=6,
        ),
        widget.WlanIw(
            format="{essid} {quality}%",
            font=FONT_TYPE,
            fontsize=13,
            interface=interface,
            background=Colours.BACKGROUND,
        ),
        _divider(),
    ]


def _bluetooth_widgets():
    if not has_bluetooth():
        return []
    return [
        widget.Image(
            margin_y=6,
            filename=f"{GRAPHICS_DIR}/bluetooth.svg",
            background=Colours.BACKGROUND,
        ),
        widget.Bluetooth(  # default adapter_paths=[] shows every adapter
            padding=8,
            fontsize=13,
            background=Colours.BACKGROUND,
        ),
        _divider(),
    ]


def _battery_widgets():
    names = batteries()
    if not names:
        return []
    widgets = []
    for name in names:
        widgets += [
            widget.BatteryIcon(
                battery=name,
                theme_path=f"{GRAPHICS_DIR}/battery_theme/",
                background=Colours.BACKGROUND,
                scale=1,
            ),
            widget.Battery(
                battery=name,
                font=FONT_TYPE,
                background=Colours.BACKGROUND,
                foreground=Colours.WHITE,
                format="{percent:2.0%}",
                fontsize=13,
                low_foreground=Colours.WARNING,
                low_percentage=0.2,
            ),
        ]
    return widgets + [_divider()]


def make_top_bar():
    return bar.Bar(
        [
            widget.Spacer(
                length=12,
                background=Colours.HIGHLIGHT,
            ),
            widget.Image(
                filename=f"{GRAPHICS_DIR}/logo.png",
                background=Colours.HIGHLIGHT,
            ),
            widget.Image(
                filename=f"{GRAPHICS_DIR}/bar_shadow_divider_up.svg",
                background=Colours.DARKER_BACKGROUND,
            ),
            widget.GroupBox(
                fontsize=18,
                borderwidth=3,
                highlight_method="border",
                active=Colours.GOLD,
                block_highlight_text_color=Colours.WHITE,
                inactive=Colours.GREY,
                background=Colours.DARKER_BACKGROUND,
                rounded=True,
                this_current_screen_border=Colours.HIGHLIGHT,
                this_screen_border=Colours.BACKGROUND,
                other_current_screen_border=Colours.BACKGROUND,
                other_screen_border=Colours.BACKGROUND,
                urgent_border=Colours.BACKGROUND,
                disable_drag=True,
                font=FONT_TYPE,
            ),
            widget.Image(
                filename=f"{GRAPHICS_DIR}/bar_shadow_divider_down.svg",
                background=Colours.DARKER_BACKGROUND,
            ),
            widget.Image(
                filename=f"{GRAPHICS_DIR}/layout.png",
                background=Colours.BACKGROUND,
            ),
            widget.CurrentLayout(
                background=Colours.BACKGROUND,
                foreground=Colours.WHITE,
                fmt="{}",
                font=FONT_TYPE,
                fontsize=13,
            ),
            widget.Image(
                filename=f"{GRAPHICS_DIR}/bar_semi_circle_right.svg",
                background=Colours.DARKER_BACKGROUND,
            ),
            widget.WindowName(
                background=Colours.DARKER_BACKGROUND,
                format="{name}",
                font=FONT_TYPE,
                foreground=Colours.WHITE,
                empty_group_string="Desktop",
                fontsize=13,
            ),
            widget.Image(
                background=Colours.DARKER_BACKGROUND,
                filename=f"{GRAPHICS_DIR}/bar_semi_circle_left.svg",
            ),
            *_wifi_widgets(),
            *_bluetooth_widgets(),
            widget.Image(
                margin_y=2,
                margin_x=2,
                filename=f"{GRAPHICS_DIR}/cpu.png",
                background=Colours.BACKGROUND,
            ),
            widget.CPU(
                format="{load_percent}%",
                foreground=Colours.WHITE,
                background=Colours.BACKGROUND,
                fontsize=13,
                max_chars=6,
            ),
            widget.Image(
                filename=f"{GRAPHICS_DIR}/bar_divider_5.svg",
                background=Colours.BACKGROUND,
            ),
            widget.Image(
                margin_y=4,
                margin_x=2,
                filename=f"{GRAPHICS_DIR}/ram.png",
                background=Colours.BACKGROUND,
            ),
            widget.Memory(
                background=Colours.BACKGROUND,
                format="{MemUsed: .0f}{mm}",
                foreground=Colours.WHITE,
                font=FONT_TYPE,
                fontsize=13,
                update_interval=5,
            ),
            widget.Image(
                filename=f"{GRAPHICS_DIR}/bar_divider_5.svg",
                background=Colours.BACKGROUND,
            ),
            *_battery_widgets(),
            widget.GenPollCommand(
                cmd="powerprofilesctl get",
                update_interval=5,
                fmt="⚡  {}",
                shell=True,
                background=Colours.BACKGROUND,
            ),
            widget.Image(
                filename=f"{GRAPHICS_DIR}/bar_divider_5.svg",
                background=Colours.BACKGROUND,
            ),
            widget.Spacer(
                length=-5,
                background=Colours.BACKGROUND,
            ),
            widget.PulseVolume(
                emoji=True,
                emoji_list=["󰝟", "󰕿", "󰖀", "󰕾"],  # muted, low, mid, high
                font=FONT_TYPE,
                background=Colours.BACKGROUND,
                foreground=Colours.WHITE,
                fontsize=16,
            ),
            widget.GenPollText(
                update_interval=2,
                func=get_audio_output_device,
                font=FONT_TYPE,
                background=Colours.BACKGROUND,
                foreground=Colours.WHITE,
                fontsize=13,
            ),
            widget.Image(
                filename=f"{GRAPHICS_DIR}/bar_divider_6.svg",
                background=Colours.BACKGROUND,
            ),
            widget.Clock(
                background=Colours.HIGHLIGHT,
                foreground=Colours.BLACK,
                font=FONT_TYPE,
                fontsize=18,
            ),
            widget.Spacer(
                length=8,
                background=Colours.HIGHLIGHT,
            ),
        ],
        size=32,
        border_width=[0, 0, 0, 0],
        margin=[10, 10, 0, 10],
    )
