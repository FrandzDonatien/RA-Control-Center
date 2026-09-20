#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Centre de contrôle — Revenue Assurance
Application desktop Tkinter (100% bibliothèque standard) avec :
  - fond en dégradé animé selon le thème
  - cartes "verre dépoli" (glassmorphism) avec halo coloré selon le statut
  - bascule thème clair / sombre
  - filtres par famille de contrôle
  - panneau de détail au clic sur une carte

Aucune dépendance externe : uniquement `tkinter` (inclus avec Python).
"""

import math
import tkinter as tk
from tkinter import font as tkfont

# ======================================================================
#  DONNÉES
# ======================================================================

STATS = [
    {"value": "12", "label": "Contrôles suivis", "status": "NEUTRE"},
    {"value": "3", "label": "En statut critique", "status": "CRITIQUE"},
    {"value": "5", "label": "En attention", "status": "ATTENTION"},
    {"value": "4", "label": "Sans anomalie", "status": "OK"},
]

FAMILIES = [
    {
        "name": "Population et complétude",
        "controls": [
            {"id": "CTRL-01", "title": "Clients actifs vs run de facturation",
             "status": "CRITIQUE", "count": 14, "unit": "éléments détectés", "freq": "Journalier"},
            {"id": "CTRL-02", "title": "Réconciliation entre cycles consécutifs",
             "status": "ATTENTION", "count": 7, "unit": "éléments détectés", "freq": "Journalier"},
        ],
    },
    {
        "name": "Exactitude du calcul",
        "controls": [
            {"id": "CTRL-03", "title": "Validation des calculs de facturation",
             "status": "OK", "count": 0, "unit": "élément détecté", "freq": "Mensuel"},
            {"id": "CTRL-04", "title": "Analyse de variance mois/mois",
             "status": "ATTENTION", "count": 1, "unit": "élément détecté", "freq": "Mensuel"},
            {"id": "CTRL-05", "title": "Validation du prorata",
             "status": "OK", "count": 2, "unit": "éléments détectés", "freq": "Journalier"},
            {"id": "CTRL-06", "title": "Facturation à 0 / hors seuils",
             "status": "CRITIQUE", "count": 9, "unit": "éléments détectés", "freq": "Journalier"},
            {"id": "CTRL-07", "title": "Montant minimum du plan",
             "status": "OK", "count": 0, "unit": "élément détecté", "freq": "Journalier"},
        ],
    },
    {
        "name": "Charges spécifiques",
        "controls": [
            {"id": "CTRL-08", "title": "Frais uniques",
             "status": "ATTENTION", "count": 5, "unit": "éléments détectés", "freq": "Journalier"},
            {"id": "CTRL-09", "title": "Usage vs facturation",
             "status": "CRITIQUE", "count": 92, "unit": "éléments détectés", "freq": "Journalier"},
            {"id": "CTRL-10", "title": "Promotions expirées",
             "status": "ATTENTION", "count": 23, "unit": "éléments détectés", "freq": "Journalier"},
        ],
    },
    {
        "name": "Revue qualitative",
        "controls": [
            {"id": "CTRL-11", "title": "Revue d'échantillon de factures",
             "status": "OK", "count": 0, "unit": "élément détecté", "freq": "Mensuel"},
            {"id": "CTRL-12", "title": "Analyse de marge / revenue assurance",
             "status": "ATTENTION", "count": 3, "unit": "éléments détectés", "freq": "Mensuel"},
        ],
    },
]

META = {"last_run": "18/09/2026 — 06:42", "env": "production"}

STATUS_COLORS = {
    "CRITIQUE": "#ff5470",
    "ATTENTION": "#ffb454",
    "OK": "#3ddc97",
    "NEUTRE": "#7aa2ff",
}

# ======================================================================
#  THÈMES
# ======================================================================

THEMES = {
    "dark": {
        "bg1": "#0e0f1a", "bg2": "#1c1836", "bg3": "#241b3e",
        "topbar": "#12101f", "footer": "#12101f",
        "text": "#f2f3f7", "text_muted": "#9a9bb5",
        "glass": "#ffffff", "glass_stipple": "gray25",
        "border": "#3a3660", "border_soft": "#2a2650",
        "chip_inactive": "#ffffff", "chip_stipple": "gray12",
        "chip_text_inactive": "#c3c4dd",
    },
    "light": {
        "bg1": "#eef1f9", "bg2": "#dfe6f5", "bg3": "#eef0fb",
        "topbar": "#ffffff", "footer": "#ffffff",
        "text": "#1c1d2e", "text_muted": "#5c5e78",
        "glass": "#ffffff", "glass_stipple": "gray25",
        "border": "#c7cbe6", "border_soft": "#d7dbf2",
        "chip_inactive": "#ffffff", "chip_stipple": "gray50",
        "chip_text_inactive": "#4c4e6b",
    },
}

ACCENT = "#7c8cff"

# ---------- constantes de mise en page ----------
PAD = 30
STAT_H = 118
STAT_GAP = 22
CHIP_H = 46
TITLE_H = 56
CARD_H = 190
CARD_GAP = 22
SECTION_GAP = 46
COLS = 3


# ======================================================================
#  UTILITAIRES COULEUR
# ======================================================================

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c))) for c in rgb)


def blend(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return rgb_to_hex((r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t))


def round_rect(canvas, x1, y1, x2, y2, r=18, **kwargs):
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


# ======================================================================
#  APPLICATION
# ======================================================================

class RevenueAssuranceApp:
    def __init__(self, root):
        self.root = root
        self.theme_name = "dark"
        self.active_filter = "Toutes les familles"
        self.selected = None
        self._resize_job = None

        root.title("Centre de contrôle — Revenue Assurance")
        root.geometry("1360x860")
        root.minsize(1040, 640)

        self.font_family = "Segoe UI"
        self.measurer = tkfont.Font(family=self.font_family, size=12, weight="bold")

        self._build_topbar()
        self._build_canvas()
        self._build_footer()
        self._apply_chrome_theme()

        root.after(80, self.render)
        self.canvas.bind("<Configure>", self._on_resize)

    # ------------------------------------------------------------------
    #  BARRE SUPÉRIEURE
    # ------------------------------------------------------------------
    def _build_topbar(self):
        self.topbar = tk.Frame(self.root, height=84)
        self.topbar.pack(side="top", fill="x")
        self.topbar.pack_propagate(False)

        left = tk.Frame(self.topbar)
        left.pack(side="left", padx=30, pady=10)
        self.title_lbl = tk.Label(left, text="Registre des contrôles",
                                   font=(self.font_family, 21, "bold"), anchor="w")
        self.title_lbl.pack(anchor="w")
        self.subtitle_lbl = tk.Label(left, text="Revenue Assurance — Facturation postpaid",
                                      font=(self.font_family, 11), anchor="w")
        self.subtitle_lbl.pack(anchor="w")

        right = tk.Frame(self.topbar)
        right.pack(side="right", padx=30, pady=10)

        info = tk.Frame(right)
        info.pack(side="left", padx=(0, 24))
        self.run_lbl = tk.Label(info, text=f"Dernière exécution : {META['last_run']}",
                                 font=(self.font_family, 10), anchor="e", justify="right")
        self.run_lbl.pack(anchor="e")
        self.env_lbl = tk.Label(info, text=f"Environnement : {META['env']}",
                                 font=(self.font_family, 10), anchor="e", justify="right")
        self.env_lbl.pack(anchor="e")

        self.toggle_canvas = tk.Canvas(right, width=150, height=40,
                                        highlightthickness=0, bd=0, cursor="hand2")
        self.toggle_canvas.pack(side="left", pady=2)
        self.toggle_canvas.bind("<Button-1>", lambda e: self.toggle_theme())
        self._draw_toggle()

    def _draw_toggle(self):
        c = self.toggle_canvas
        c.delete("all")
        theme = THEMES[self.theme_name]
        dark = self.theme_name == "dark"
        track_fill = "#2b2750" if dark else "#dfe3f5"
        round_rect(c, 34, 6, 150, 34, r=14, fill=track_fill, outline=theme["border"], width=1)
        knob_x = 46 if dark else 138
        glow = ACCENT if dark else "#ffb454"
        c.create_oval(knob_x - 16, 4, knob_x + 16, 36, fill=glow, outline="", stipple="gray50")
        c.create_oval(knob_x - 12, 8, knob_x + 12, 32, fill="#ffffff" if dark else "#fff6e0",
                       outline=glow, width=2)
        c.create_text(0, 20, anchor="w",
                       text=("Sombre" if dark else "Clair"),
                       font=(self.font_family, 10, "bold"),
                       fill=theme["text"])

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self._apply_chrome_theme()
        self.render()

    def _apply_chrome_theme(self):
        t = THEMES[self.theme_name]
        self.topbar.configure(bg=t["topbar"])
        for w in self.topbar.winfo_children():
            w.configure(bg=t["topbar"])
            for c in w.winfo_children():
                c.configure(bg=t["topbar"])
        self.title_lbl.configure(bg=t["topbar"], fg=t["text"])
        self.subtitle_lbl.configure(bg=t["topbar"], fg=t["text_muted"])
        self.run_lbl.configure(bg=t["topbar"], fg=t["text_muted"])
        self.env_lbl.configure(bg=t["topbar"], fg=t["text_muted"])
        self.toggle_canvas.configure(bg=t["topbar"])
        self._draw_toggle()

        self.footer.configure(bg=t["footer"])
        self.footer_lbl.configure(bg=t["footer"], fg=t["text_muted"])
        self.canvas.configure(bg=t["bg1"])

    # ------------------------------------------------------------------
    #  CANVAS PRINCIPAL (zone défilante)
    # ------------------------------------------------------------------
    def _build_canvas(self):
        wrapper = tk.Frame(self.root)
        wrapper.pack(side="top", fill="both", expand=True)

        self.canvas = tk.Canvas(wrapper, highlightthickness=0, bd=0)
        self.vscroll = tk.Scrollbar(wrapper, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscroll.set)
        self.vscroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if getattr(event, "num", None) == 4:
            self.canvas.yview_scroll(-3, "units")
        elif getattr(event, "num", None) == 5:
            self.canvas.yview_scroll(3, "units")
        else:
            self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def _on_resize(self, event):
        if self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(120, self.render)

    # ------------------------------------------------------------------
    #  BARRE INFÉRIEURE (détail de la sélection)
    # ------------------------------------------------------------------
    def _build_footer(self):
        self.footer = tk.Frame(self.root, height=46)
        self.footer.pack(side="bottom", fill="x")
        self.footer.pack_propagate(False)
        self.footer_lbl = tk.Label(
            self.footer,
            text="Sélectionnez un contrôle pour afficher le détail.",
            font=(self.font_family, 10), anchor="w"
        )
        self.footer_lbl.pack(side="left", padx=28)

    def _update_footer(self, ctrl, family_name):
        self.footer_lbl.configure(
            text=(f"{ctrl['id']}  ·  {ctrl['title']}  ·  Famille : {family_name}  ·  "
                  f"Statut : {ctrl['status']}  ·  {ctrl['count']} {ctrl['unit']}  ·  "
                  f"Fréquence : {ctrl['freq']}")
        )

    # ------------------------------------------------------------------
    #  DÉGRADÉ DE FOND
    # ------------------------------------------------------------------
    def _draw_gradient(self, w, h, c1, c2, c3):
        step = 3
        half = h / 2 if h else 1
        for y in range(0, int(h) + step, step):
            t = min(1.0, y / half) if half else 0
            color = blend(c1, c2, t) if y <= half else blend(c2, c3, min(1.0, (y - half) / half))
            self.canvas.create_line(0, y, w, y, fill=color, width=step + 1)

    # ------------------------------------------------------------------
    #  RENDU COMPLET
    # ------------------------------------------------------------------
    def render(self):
        cw = self.canvas.winfo_width()
        if cw < 60:
            self.root.after(60, self.render)
            return
        self.canvas.delete("all")
        t = THEMES[self.theme_name]

        y = PAD
        y += STAT_H + SECTION_GAP - 6   # stats
        y += CHIP_H + SECTION_GAP - 10  # filtres

        visible_families = [f for f in FAMILIES
                             if self.active_filter in ("Toutes les familles", f["name"])]

        family_layout = []
        for fam in visible_families:
            title_y = y
            y += TITLE_H
            n = len(fam["controls"])
            rows = math.ceil(n / COLS)
            grid_y = y
            y += rows * (CARD_H + CARD_GAP) - CARD_GAP + SECTION_GAP
            family_layout.append((fam, title_y, grid_y, rows))

        total_h = y + PAD

        self._draw_gradient(cw, total_h, t["bg1"], t["bg2"], t["bg3"])

        yy = PAD
        self._draw_stats(yy, cw, t)
        yy += STAT_H + SECTION_GAP - 6
        self._draw_filters(yy, cw, t)

        for fam, title_y, grid_y, rows in family_layout:
            self._draw_family_title(fam["name"], title_y, cw, t)
            self._draw_family_cards(fam, grid_y, cw, t)

        self.canvas.configure(scrollregion=(0, 0, cw, total_h))

    # ------------------------------------------------------------------
    #  BLOC STATISTIQUES
    # ------------------------------------------------------------------
    def _draw_stats(self, y, cw, t):
        avail = cw - 2 * PAD
        n = len(STATS)
        w = (avail - STAT_GAP * (n - 1)) / n
        for i, s in enumerate(STATS):
            x1 = PAD + i * (w + STAT_GAP)
            x2 = x1 + w
            y2 = y + STAT_H
            color = STATUS_COLORS[s["status"]]

            round_rect(self.canvas, x1 - 2, y - 2, x2 + 2, y2 + 2, r=20,
                       fill=color, outline="", stipple="gray75")
            round_rect(self.canvas, x1, y, x2, y2, r=18,
                       fill=t["glass"], stipple=t["glass_stipple"],
                       outline=t["border"], width=1.4)

            dot_r = 6
            self.canvas.create_oval(x1 + 20, y + 20 - dot_r, x1 + 20 + 2 * dot_r, y + 20 + dot_r,
                                     fill=color, outline="")
            self.canvas.create_text(x1 + 20, y + STAT_H / 2 + 6, anchor="w",
                                     text=s["value"], font=(self.font_family, 30, "bold"),
                                     fill=t["text"])
            self.canvas.create_text(x1 + w - 16, y + STAT_H / 2 + 10, anchor="e",
                                     text=s["label"], font=(self.font_family, 11),
                                     fill=t["text_muted"], width=w - 60, justify="right")

    # ------------------------------------------------------------------
    #  FILTRES (chips)
    # ------------------------------------------------------------------
    def _draw_filters(self, y, cw, t):
        labels = ["Toutes les familles"] + [f["name"] for f in FAMILIES]
        x = PAD
        y2 = y + CHIP_H
        for label in labels:
            tw = self.measurer.measure(label)
            pill_w = tw + 44
            active = (label == self.active_filter)

            tag = f"chip::{label}"
            if active:
                round_rect(self.canvas, x - 2, y - 2, x + pill_w + 2, y2 + 2, r=20,
                           fill=ACCENT, outline="", stipple="gray50", tags=(tag,))
                round_rect(self.canvas, x, y, x + pill_w, y2, r=18,
                           fill=ACCENT, outline="", tags=(tag,))
                fg = "#ffffff"
            else:
                round_rect(self.canvas, x, y, x + pill_w, y2, r=18,
                           fill=t["chip_inactive"], stipple=t["chip_stipple"],
                           outline=t["border"], width=1.2, tags=(tag,))
                fg = t["chip_text_inactive"]

            self.canvas.create_text((x + x + pill_w) / 2, (y + y2) / 2, text=label,
                                     font=(self.font_family, 10, "bold"), fill=fg, tags=(tag,))

            self.canvas.tag_bind(tag, "<Button-1>", lambda e, lbl=label: self._set_filter(lbl))
            self.canvas.tag_bind(tag, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
            self.canvas.tag_bind(tag, "<Leave>", lambda e: self.canvas.config(cursor=""))

            x += pill_w + 14

    def _set_filter(self, label):
        self.active_filter = label
        self.render()

    # ------------------------------------------------------------------
    #  TITRE DE FAMILLE
    # ------------------------------------------------------------------
    def _draw_family_title(self, name, y, cw, t):
        self.canvas.create_text(PAD, y + 6, anchor="nw", text=name,
                                 font=(self.font_family, 15, "bold"), fill=t["text"])
        line_y = y + 34
        self.canvas.create_line(PAD, line_y, cw - PAD, line_y, fill=t["border_soft"], width=1)

    # ------------------------------------------------------------------
    #  GRILLE DE CARTES D'UNE FAMILLE
    # ------------------------------------------------------------------
    def _draw_family_cards(self, fam, y0, cw, t):
        avail = cw - 2 * PAD
        card_w = (avail - CARD_GAP * (COLS - 1)) / COLS
        for i, ctrl in enumerate(fam["controls"]):
            row, col = divmod(i, COLS)
            x = PAD + col * (card_w + CARD_GAP)
            y = y0 + row * (CARD_H + CARD_GAP)
            self._draw_card(x, y, card_w, CARD_H, ctrl, fam["name"], t)

    def _draw_card(self, x, y, w, h, ctrl, family_name, t):
        status = ctrl["status"]
        color = STATUS_COLORS[status]
        selected = (self.selected == ctrl["id"])
        tag = f"card::{ctrl['id']}"

        # halo coloré (glow) derrière la carte
        round_rect(self.canvas, x - 4, y - 4, x + w + 4, y + h + 4, r=24,
                   fill=color, outline="", stipple="gray75", tags=(tag,))

        # carte "verre"
        round_rect(self.canvas, x, y, x + w, y + h, r=20,
                   fill=t["glass"], stipple=t["glass_stipple"],
                   outline=(color if selected else t["border"]),
                   width=(2.6 if selected else 1.3), tags=(tag,))

        # bandeau supérieur fin (accent)
        round_rect(self.canvas, x + 14, y + 14, x + 14 + 28, y + 18, r=2,
                   fill=color, outline="", tags=(tag,))

        # identifiant
        self.canvas.create_text(x + 20, y + 30, anchor="w", text=ctrl["id"],
                                 font=(self.font_family, 10, "bold"),
                                 fill=t["text_muted"], tags=(tag,))

        # badge de statut
        badge_txt = status
        badge_w = self.measurer.measure(badge_txt) + 24
        bx2 = x + w - 16
        bx1 = bx2 - badge_w
        round_rect(self.canvas, bx1, y + 16, bx2, y + 38, r=11,
                   fill=color, outline="", tags=(tag,))
        self.canvas.create_text((bx1 + bx2) / 2, y + 27, text=badge_txt,
                                 font=(self.font_family, 9, "bold"),
                                 fill="#141225", tags=(tag,))

        # titre (wrap)
        self.canvas.create_text(x + 20, y + 52, anchor="nw", text=ctrl["title"],
                                 font=(self.font_family, 12, "bold"), fill=t["text"],
                                 width=w - 40, tags=(tag,))

        # nombre d'éléments
        self.canvas.create_text(x + 20, y + h - 52, anchor="sw", text=str(ctrl["count"]),
                                 font=(self.font_family, 24, "bold"), fill=color, tags=(tag,))
        self.canvas.create_text(x + 20, y + h - 30, anchor="sw", text=ctrl["unit"],
                                 font=(self.font_family, 9), fill=t["text_muted"], tags=(tag,))

        # fréquence
        self.canvas.create_text(x + w - 20, y + h - 20, anchor="se", text=ctrl["freq"],
                                 font=(self.font_family, 9, "bold"), fill=t["text_muted"],
                                 tags=(tag,))

        self.canvas.tag_bind(tag, "<Button-1>",
                              lambda e, c=ctrl, fn=family_name: self._select_card(c, fn))
        self.canvas.tag_bind(tag, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(tag, "<Leave>", lambda e: self.canvas.config(cursor=""))

    def _select_card(self, ctrl, family_name):
        self.selected = ctrl["id"]
        self._update_footer(ctrl, family_name)
        self.render()


# ======================================================================
#  POINT D'ENTRÉE
# ======================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = RevenueAssuranceApp(root)
    root.mainloop()