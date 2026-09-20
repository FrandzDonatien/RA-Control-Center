import tkinter as tk
from config import COLORS


class TrendChart(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["panel"], highlightthickness=0, **kwargs)

    def draw(self, points):
        self.delete("all")
        if not points:
            self.create_text(200, 70, text="Aucune tendance disponible",
                             fill=COLORS["muted"], font=("Segoe UI", 10))
            return

        self.update_idletasks()
        w = max(self.winfo_width(), 360)
        h = max(self.winfo_height(), 150)
        pad_l, pad_r, pad_t, pad_b = 28, 14, 15, 25
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b
        max_v = max(max(p["nb_items"] for p in points), 1)

        n = len(points)
        step = plot_w / max(n, 1)
        bar_w = min(45, step * 0.68)

        for i, p in enumerate(points):
            x = pad_l + step * i + step / 2
            bh = (p["nb_items"] / max_v) * (plot_h - 12)
            y = pad_t + plot_h - bh
            fill = COLORS["critical"] if i == n - 1 and p["nb_items"] > 0 else COLORS["panel_2"]
            self.create_rectangle(x - bar_w/2, y, x + bar_w/2,
                                  pad_t + plot_h, fill=fill, outline="")
            self.create_text(x, y - 8, text=str(p["nb_items"]),
                             fill=COLORS["muted"], font=("Segoe UI", 8))
            label = p["date_controle"].strftime("%d/%m")
            self.create_text(x, pad_t + plot_h + 14, text=label,
                             fill=COLORS["muted"], font=("Segoe UI", 8))

    def redraw(self, points):
        self.draw(points)
