import tkinter as tk
from config import COLORS


def make_label(parent, text="", size=10, bold=False, color=None, **kwargs):
    font = ("Segoe UI", size, "bold" if bold else "normal")
    return tk.Label(
        parent, text=text, font=font,
        bg=kwargs.pop("bg", COLORS["bg"]),
        fg=color or COLORS["text"],
        **kwargs
    )
