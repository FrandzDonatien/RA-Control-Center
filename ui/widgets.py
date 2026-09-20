import tkinter as tk
from config import COLORS


def status_colors(status):
    return {
        "CRITIQUE": (COLORS["critical"], COLORS["critical_bg"]),
        "ATTENTION": (COLORS["attention"], COLORS["attention_bg"]),
        "OK": (COLORS["ok"], COLORS["ok_bg"]),
    }.get(status, (COLORS["muted"], COLORS["panel"]))


class StatCard(tk.Frame):
    def __init__(self, parent, value, title, status=None):
        super().__init__(parent, bg=COLORS["panel"], highlightbackground=COLORS["border"],
                         highlightthickness=1)
        color = status_colors(status)[0] if status else COLORS["text"]
        tk.Label(self, text=value, font=("Segoe UI", 23, "bold"),
                 bg=COLORS["panel"], fg=color).pack(anchor="w", padx=18, pady=(13, 0))
        tk.Label(self, text=title, font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg="#a7abb4").pack(anchor="w", padx=18, pady=(0, 13))


class ControlCard(tk.Frame):
    def __init__(self, parent, card, on_click):
        super().__init__(parent, bg=COLORS["panel"], highlightthickness=1,
                         highlightbackground=COLORS["border"], cursor="hand2")
        self.card = card
        self.on_click = on_click

        accent, badge_bg = status_colors(card.severite)
        self.configure(highlightbackground=accent)

        top = tk.Frame(self, bg=COLORS["panel"])
        top.pack(fill="x", padx=14, pady=(11, 0))

        tk.Label(top, text=f"CTRL-{card.control_id:02d}", font=("Consolas", 12),
                 bg=COLORS["panel"], fg="#737986").pack(side="left")
        tk.Label(top, text=card.severite, font=("Segoe UI", 13, "bold"),
                 bg=badge_bg, fg=accent, padx=7, pady=3).pack(side="right")

        tk.Label(self, text=card.control_name, font=("Segoe UI", 14, "bold"),
                 bg=COLORS["panel"], fg=COLORS["text"], anchor="w",
                 justify="left", wraplength=220).pack(fill="x", padx=14, pady=(9, 5))

        tk.Label(self, text=str(card.nb_items), font=("Segoe UI", 18, "bold"),
                 bg=COLORS["panel"], fg=COLORS["text"]).pack(anchor="w", padx=14)
        tk.Label(self, text="éléments détectés", font=("Segoe UI", 8),
                 bg=COLORS["panel"], fg="#727782").pack(anchor="w", padx=14)

        bottom = tk.Frame(self, bg=COLORS["panel"])
        bottom.pack(fill="x", padx=14, pady=(2, 11))
        tk.Label(bottom, text=card.frequence, font=("Segoe UI", 8),
                 bg=COLORS["panel"], fg="#7f848e").pack(side="right")

        self.bind("<Button-1>", self._click_all)
        for child in self.winfo_children():
            child.bind("<Button-1>", self._click_all)
            for sub in child.winfo_children():
                sub.bind("<Button-1>", self._click_all)

    def _click_all(self, _event):
        self.on_click(self.card)
