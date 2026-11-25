import os

FONT_TYPE = "JetBrains Mono Bold"

# Resolved from this file, so it works wherever the config lives.
GRAPHICS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphics")


class Colours:
    GREY = "#696969"
    GOLD = "#e2c779"
    HIGHLIGHT = "#00BFFF"
    BRIGHT_GREEN = "#7ee787"
    BACKGROUND = "#1b1e37"
    BACKGROUND_LIGHT = "#f48077"
    DARKER_BACKGROUND = "#030b1e"
    WHITE = "#e1e1e2"
    BLACK = "#000000"
    WARNING = "#f6719b"
    PURPLE = "#c792ea"
