"""Icônes dessinées avec Pillow (pas d'emoji, pas de police externe)."""

import customtkinter as ctk
from PIL import Image, ImageDraw

_ICON_CACHE = {}


def _draw_icon(name, color, size):
    S = 16
    N = 24 * S
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w = int(1.9 * S)

    def P(*pts):
        return [(x * S, y * S) for x, y in pts]

    def line(*pts):
        d.line(P(*pts), fill=color, width=w, joint="curve")
        r = w / 2
        for x, y in P(*pts):
            d.ellipse((x - r, y - r, x + r, y + r), fill=color)

    def dot(x, y, r=1.2):
        d.ellipse(P((x - r, y - r), (x + r, y + r)), fill=color)

    def circle():
        d.ellipse(P((3, 3), (21, 21)), outline=color, width=w)

    if name == "home":
        line((3, 11), (12, 3.5), (21, 11))
        line((5.5, 9.5), (5.5, 20), (18.5, 20), (18.5, 9.5))
        d.rounded_rectangle(P((10, 14), (14, 20)), radius=1 * S, outline=color, width=w)

    elif name == "list":
        for y in (6, 12, 18):
            line((9, y), (20, y))
            dot(4.5, y, 1.3)

    elif name == "layers":
        line((12, 3), (21, 8), (12, 13), (3, 8), (12, 3))
        line((3, 12.5), (12, 17.5), (21, 12.5))
        line((3, 16.5), (12, 21.5), (21, 16.5))

    elif name == "chart":
        line((6, 20), (6, 12))
        line((12, 20), (12, 5))
        line((18, 20), (18, 9))

    elif name == "search":
        d.ellipse(P((4, 4), (17, 17)), outline=color, width=w)
        line((15.5, 15.5), (20, 20))

    elif name == "refresh":
        d.arc(P((4, 4), (20, 20)), start=40, end=310, fill=color, width=w)
        d.polygon(P((19.2, 7.6), (18.8, 3.6), (15.4, 7.8)), fill=color)

    elif name == "arrow_left":
        line((19, 12), (5, 12))
        line((11, 6), (5, 12), (11, 18))

    elif name == "close":
        line((6, 6), (18, 18))
        line((18, 6), (6, 18))

    elif name == "alert":
        line((12, 3.8), (21, 19.5), (3, 19.5), (12, 3.8))
        line((12, 10), (12, 14))
        dot(12, 17, 0.9)

    elif name == "warning":
        circle()
        line((12, 7.5), (12, 12.5))
        dot(12, 16.3, 0.9)

    elif name == "check_circle":
        circle()
        line((8, 12.3), (11, 15.3), (16.2, 9))

    elif name == "money":
        d.rounded_rectangle(P((2.5, 6), (21.5, 18)), radius=2 * S, outline=color, width=w)
        d.ellipse(P((9, 9), (15, 15)), outline=color, width=w)
        dot(5.8, 12, 0.9)
        dot(18.2, 12, 0.9)

    elif name == "clock":
        circle()
        line((12, 7), (12, 12), (16, 14))

    elif name == "logo":
        d.rounded_rectangle((0, 0, N - 1, N - 1), radius=6 * S, fill=color)
        white = (255, 255, 255, 255)
        pts = P((7, 12.5), (10.6, 16), (17, 8.5))
        d.line(pts, fill=white, width=int(2.4 * S), joint="curve")
        for x, y in (pts[0], pts[-1]):
            r = 1.2 * S
            d.ellipse((x - r, y - r, x + r, y + r), fill=white)

    return img.resize((size * 4, size * 4), Image.LANCZOS)


def icon(name, color, size=20):
    key = (name, color, size)
    if key not in _ICON_CACHE:
        img = _draw_icon(name, color, size)
        _ICON_CACHE[key] = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
    return _ICON_CACHE[key]