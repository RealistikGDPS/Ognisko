from __future__ import annotations


class RGB:
    def __init__(self, r: int, g: int, b: int) -> None:
        self.r = r
        self.g = g
        self.b = b

    @staticmethod
    def from_str(text: str) -> RGB | None:
        text = text.lower()
        if text in COLOUR_PRESETS:
            return COLOUR_PRESETS[text]

        text_split = text.strip(" ").split(",", maxsplit=3)
        if len(text_split) != 3:
            return None

        r, g, b = text_split
        if not r.isdigit() or not g.isdigit() or b.isdigit():
            return None

        return RGB(r=int(r), g=int(g), b=int(b))

    def __str__(self) -> str:
        return f"{self.r},{self.g},{self.b}"


COLOUR_PRESETS: dict[str, RGB] = {
    "red": RGB(235, 64, 52),
    "blue": RGB(66, 135, 245),
    "yellow": RGB(252, 186, 3),
    "green": RGB(50, 168, 82),
    "blush": RGB(255, 204, 229),
    "cream": RGB(255, 229, 204),
    "turquoise": RGB(204, 229, 255),
    "mint": RGB(204, 255, 235),
    "gold": RGB(255, 236, 153),
    "black": RGB(0, 0, 0),
}
