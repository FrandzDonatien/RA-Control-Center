import tkinter as tk

# Couleurs fixes (fond blanc, aucun noir) -- indépendantes de la palette
BG = "#FFFFFF"
BAR = "#9DB6F2"          # barres normales : bleu clair bien visible
BAR_LAST = "#E5484D"     # dernière exécution (si > 0) : rouge
BAR_LAST_OK = "#2F5FE0"  # dernière exécution à 0 : bleu accent
GRID = "#E9ECF1"
BASE = "#C9CED6"
VALUE = "#2A2F3A"        # gris anthracite (lisible, pas noir pur)
LABEL = "#6B7280"


class TrendChart(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, highlightthickness=0, bd=0, **kwargs)
        self._points = []
        self.bind("<Configure>", lambda e: self.draw(self._points))

    def draw(self, points):
        self._points = points or []
        self.delete("all")

        w = max(self.winfo_width(), 360)
        h = max(self.winfo_height(), 150)

        if not self._points:
            self.create_text(w // 2, h // 2, text="Aucune tendance disponible",
                             fill=LABEL, font=("Segoe UI", 10))
            return

        pad_l, pad_r, pad_t, pad_b = 28, 14, 26, 28
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b
        max_v = max(max(p["nb_items"] for p in self._points), 1)

        n = len(self._points)
        step = plot_w / max(n, 1)
        bar_w = min(45, step * 0.68)
        base_y = pad_t + plot_h

        # lignes de repère horizontales
        for frac in (0.25, 0.5, 0.75, 1.0):
            gy = base_y - frac * (plot_h - 12)
            self.create_line(pad_l, gy, w - pad_r, gy, fill=GRID)

        # ligne de base
        self.create_line(pad_l, base_y, w - pad_r, base_y, fill=BASE, width=1)

        for i, p in enumerate(self._points):
            x = pad_l + step * i + step / 2
            bh = (p["nb_items"] / max_v) * (plot_h - 12)
            y = base_y - bh
            is_last = i == n - 1

            if is_last:
                fill = BAR_LAST if p["nb_items"] > 0 else BAR_LAST_OK
            else:
                fill = BAR

            # barre (hauteur minimale de 3 px pour rester visible à 0)
            self.create_rectangle(x - bar_w / 2, min(y, base_y - 3),
                                  x + bar_w / 2, base_y,
                                  fill=fill, outline="")

            self.create_text(x, min(y, base_y - 3) - 9, text=str(p["nb_items"]),
                             fill=VALUE, font=("Segoe UI", 9, "bold"))

            label = p["date_controle"].strftime("%d/%m")
            self.create_text(x, base_y + 14, text=label,
                             fill=LABEL, font=("Segoe UI", 8))

    def redraw(self, points):
        self.draw(points)