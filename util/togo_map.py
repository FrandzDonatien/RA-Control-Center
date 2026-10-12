"""Carte interactive du Togo (Canvas Tkinter).

- Molette : zoom centré sur la souris
- Glisser (clic gauche) : déplacer
- Double-clic : zoom avant
- Boutons + / − / ⟲
- À partir de DETAIL_ZOOM, chaque ville montre ses points de détail
"""

import tkinter as tk
from math import sqrt

from util.theme import T, fmt
from util.boundaries import TOGO_OUTLINE

# Limites calculées à partir des frontières réelles du Togo
LONGITUDES = [lon for lon, lat in TOGO_OUTLINE]
LATITUDES = [lat for lon, lat in TOGO_OUTLINE]

MARGIN_LON = 0.08
MARGIN_LAT = 0.15

LON0 = min(LONGITUDES) - MARGIN_LON
LON1 = max(LONGITUDES) + MARGIN_LON
LAT0 = min(LATITUDES) - MARGIN_LAT
LAT1 = max(LATITUDES) + MARGIN_LAT

LABEL_SIDE = {"Lomé": "w", "Kpalimé": "w", "Tsévié": "w"}


class TogoMap(tk.Canvas):

    MIN_ZOOM, MAX_ZOOM = 1.0, 40.0
    DETAIL_ZOOM = 2.5   # zoom à partir duquel on voit les points
    LABEL_ZOOM = 4.0    # zoom à partir duquel les noms des points s'affichent

    def __init__(self, parent, zones, height=450, font="Segoe UI",
                 scroll_parent=None):
        super().__init__(parent, height=height, bg=T["card"], highlightthickness=0)
        self.zones = zones
        self.font = font
        self.scroll_parent = scroll_parent  # CTkScrollableFrame à neutraliser
        self.hit = []
        self.zoom, self.tx, self.ty = 1.0, 0.0, 0.0
        self._drag = None
        self._moved = False

        self.bind("<Configure>", lambda e: self.draw())
        self.bind("<Motion>", self._on_move)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<B1-Motion>", self._drag_move)
        self.bind("<ButtonRelease-1>", self._release)
        self.bind("<Double-Button-1>", lambda e: self._zoom_at(e.x, e.y, 2.0))
        self.bind("<MouseWheel>", self._wheel)                            # Windows / macOS
        self.bind("<Button-4>", lambda e: self._zoom_at(e.x, e.y, 1.25))  # Linux
        self.bind("<Button-5>", lambda e: self._zoom_at(e.x, e.y, 0.8))

        self._build_buttons()

    # ---------------- boutons ----------------
    def _build_buttons(self):
        box = tk.Frame(self, bg=T["card"])
        box.place(relx=1.0, x=-8, y=8, anchor="ne")
        kw = dict(width=2, relief="flat", bg=T["gray100"], fg=T["text_soft"],
                  activebackground=T["brand_50"], bd=0, cursor="hand2",
                  font=(self.font, 11, "bold"))
        tk.Button(box, text="+", command=lambda: self._zoom_center(1.6), **kw).pack(pady=(0, 2))
        tk.Button(box, text="−", command=lambda: self._zoom_center(1 / 1.6), **kw).pack(pady=(0, 2))
        tk.Button(box, text="⟲", command=self.reset_view, **kw).pack()

    # ---------------- vue (zoom / pan) ----------------
    def reset_view(self):
        self.zoom, self.tx, self.ty = 1.0, 0.0, 0.0
        self.draw()

    def _zoom_center(self, k):
        self._zoom_at(self.winfo_width() / 2, self.winfo_height() / 2, k)

    def _zoom_at(self, mx, my, k):
        new = min(max(self.zoom * k, self.MIN_ZOOM), self.MAX_ZOOM)
        k = new / self.zoom
        if k == 1:
            return
        self.tx = mx - (mx - self.tx) * k   # le point sous la souris reste fixe
        self.ty = my - (my - self.ty) * k
        self.zoom = new
        self._clamp()
        self.draw()

    def _clamp(self):
        w, h = self.winfo_width(), self.winfo_height()
        self.tx = min(max(self.tx, w * (1 - self.zoom)), 0)
        self.ty = min(max(self.ty, h * (1 - self.zoom)), 0)

    def _wheel(self, e):
        self._zoom_at(e.x, e.y, 1.25 if e.delta > 0 else 0.8)

    def _press(self, e):
        self._drag = (e.x, e.y, self.tx, self.ty)
        self._moved = False

    def _drag_move(self, e):
        if not self._drag:
            return
        x0, y0, tx0, ty0 = self._drag
        if abs(e.x - x0) + abs(e.y - y0) > 3:
            self._moved = True
            self.configure(cursor="fleur")
        self.tx = tx0 + e.x - x0
        self.ty = ty0 + e.y - y0
        self._clamp()
        self.draw()

    def _release(self, e):
        self._drag = None
        self.configure(cursor="")

    # ---------------- molette vs page défilante ----------------
    def _on_enter(self, e):
        sp = self.scroll_parent
        if sp is not None and hasattr(sp, "_parent_canvas"):
            sp._parent_canvas.yview = lambda *a, **k: (0.0, 1.0) if not a else None

    def _on_leave(self, e):
        self.delete("tip")
        self.configure(cursor="")
        sp = self.scroll_parent
        if sp is not None and hasattr(sp, "_parent_canvas"):
            cv = sp._parent_canvas
            if "yview" in cv.__dict__:
                del cv.yview

    # ---------------- projection ----------------
    def _project(self, lon, lat):
        bx = self.ox + (lon - LON0) * self.s
        by = self.oy + (LAT1 - lat) * self.s
        return bx * self.zoom + self.tx, by * self.zoom + self.ty

    # ---------------- dessin ----------------
    def draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 80 or h < 80:
            return
        F = self.font

        pad = 8
        self.s = min((w - 2 * pad) / (LON1 - LON0), (h - 2 * pad) / (LAT1 - LAT0))
        self.ox = (w - self.s * (LON1 - LON0)) / 2
        self.oy = (h - self.s * (LAT1 - LAT0)) / 2

        for text, lon, lat, anchor in [
            ("GHANA", 0.30, 8.00, "e"), ("BÉNIN", 1.92, 7.90, "w"),
            ("BURKINA FASO", 0.50, 11.28, "center"),
            ("Golfe de Guinée", 1.20, 5.95, "center"),
        ]:
            x, y = self._project(lon, lat)
            self.create_text(x, y, text=text, anchor=anchor, fill=T["gray300"],
                             font=(F, 8, "bold"))

        flat = [c for lon, lat in TOGO_OUTLINE for c in self._project(lon, lat)]
        self.create_polygon(*flat, fill=T["brand_50"], outline=T["brand_300"],
                            width=1.5, joinstyle="round")

        detail = self.zoom >= self.DETAIL_ZOOM
        show_names = self.zoom >= self.LABEL_ZOOM
        vmax = max(z["amount"] for z in self.zones)
        self.hit = []

        for z in sorted(self.zones, key=lambda z: -z["amount"]):
            x, y = self._project(z["lon"], z["lat"])
            r = 4 + 11 * sqrt(z["amount"] / vmax)
            spots = z.get("spots") or []

            if detail and spots:
                # mode détail : anneau de la ville + points
                self.create_oval(x - 6, y - 6, x + 6, y + 6, outline=T["brand"],
                                 width=2, dash=(2, 2))
                smax = max(sp["amount"] for sp in spots)
                for sp in spots:
                    sx, sy = self._project(sp["lon"], sp["lat"])
                    sr = 4 + 6 * sqrt(sp["amount"] / smax)
                    self.create_oval(sx - sr - 3, sy - sr - 3, sx + sr + 3, sy + sr + 3,
                                     fill=T["brand_200"], outline="")
                    self.create_oval(sx - sr, sy - sr, sx + sr, sy + sr,
                                     fill=T["brand"], outline=T["card"], width=2)
                    self.hit.append((sx, sy, sr + 3, sp, z["name"]))
                    if show_names:
                        self.create_text(sx + sr + 6, sy, text=sp["name"], anchor="w",
                                         fill=T["text_soft"], font=(F, 8))
                self.create_text(x, y - 12, text=z["name"], anchor="s",
                                 fill=T["text"], font=(F, 10, "bold"))
            else:
                # mode global : bulle de la ville
                self.create_oval(x - r - 4, y - r - 4, x + r + 4, y + r + 4,
                                 fill=T["brand_200"], outline="")
                self.create_oval(x - r, y - r, x + r, y + r, fill=T["brand"],
                                 outline=T["card"], width=2)
                self.hit.append((x, y, r + 4, z, None))

                side = LABEL_SIDE.get(z["name"], "e")
                dx = (r + 8) * (-1 if side == "w" else 1)
                self.create_text(x + dx, y, text=z["name"], anchor=side,
                                 fill=T["text_soft"], font=(F, 8, "bold"))

        self.create_text(8, h - 8, anchor="sw", fill=T["muted"], font=(F, 8),
                         text=f"Molette : zoom · Glisser : déplacer · ×{self.zoom:.1f}")

    # ---------------- infobulle ----------------
    def _on_move(self, event):
        if self._drag and self._moved:
            return
        self.delete("tip")
        F = self.font
        for x, y, r, item, parent_name in reversed(self.hit):
            if (event.x - x) ** 2 + (event.y - y) ** 2 <= r * r:
                self.configure(cursor="hand2")
                title = item["name"] if parent_name is None \
                    else f"{item['name']} ({parent_name})"
                lines = [title, f"{fmt(item['amount'])} FCFA",
                         f"{fmt(item['recharges'])} recharges"]
                tw = max(len(s) for s in lines) * 6.4 + 18
                th = 17 * len(lines) + 10
                x0 = min(max(x + 14, 4), self.winfo_width() - tw - 4)
                y0 = min(max(y - th / 2, 4), self.winfo_height() - th - 4)
                self.create_rectangle(x0, y0, x0 + tw, y0 + th, fill=T["text"],
                                      outline="", tags="tip")
                for k, line in enumerate(lines):
                    self.create_text(
                        x0 + 9, y0 + 14 + 17 * k, text=line, anchor="w",
                        fill="white" if k else "#C2D6FF",
                        font=(F, 9, "bold" if k == 0 else "normal"),
                        tags="tip")
                return
        self.configure(cursor="")