from typing import Dict

FONT_TYPE = "JetBrains Mono Bold"


class ColourEnum:
    _colours: Dict[str, str] = {}

    def __init_subclass__(cls):
        for name, hex_value in cls.__annotations__.items():
            if isinstance(hex_value, str) and hex_value.startswith("#"):
                cls._colours[name] = hex_value

    def __getattr__(self, name: str) -> str:
        if name in self._colours:
            return self._colours[name]
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )


class Colours(ColourEnum):
    GREY = "#696969"
    GOLD = "#e2c779"
    HIGHLIGHT = "#ff6b8a"
    BRIGHT_GREEN = "#7ee787"
    BACKGROUND = "#1b1e37"
    BACKGROUND_LIGHT = "#f48077"
    DARKER_BACKGROUND = "#030b1e"
    WHITE = "#e1e1e2"
    BLACK = "#000000"
    WARNING = "#f6719b"
