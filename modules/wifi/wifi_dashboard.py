import tkinter as tk
import tkinter.font as tkfont
from math import floor, log10
from statistics import median

import customtkinter as ctk

from ui.icons import icon
from ui.palette import FONT as BASE_FONT
from util.theme import T, fmt
from util.togo_map import TogoMap
from util.spots import make_spots

UI_FONT = BASE_FONT  # remplacé par "Outfit" si la police est installée


def nice_ticks(vmax, count=5):
    if vmax <= 0:
        return [0, 1]
    raw = vmax / count
    mag = 10 ** floor(log10(raw))
    step = mag
    for m in (1, 2, 2.5, 5, 10):
        step = m * mag
        if step * count >= vmax:
            break
    return [step * i for i in range(count + 1)]


# =================================================================
# BRIQUES UI
# =================================================================

def make_card(parent, **kw):
    return ctk.CTkFrame(
        parent, fg_color=T["card"], corner_radius=16,
        border_width=1, border_color=T["border"], **kw
    )


def make_pill(parent, text, fg, bg, width=None, height=24, size=11):
    return ctk.CTkLabel(
        parent, text=text, text_color=fg, fg_color=bg, corner_radius=height // 2,
        height=height, width=width or 0,
        font=ctk.CTkFont(family=UI_FONT, size=size, weight="bold")
    )


# =================================================================
# GRAPHIQUES (Canvas)
# =================================================================

class Chart(tk.Canvas):
    """Histogramme ou courbe avec grille pointillée et infobulle au survol."""

    def __init__(self, parent, labels, values, kind="bar", height=230,
                 highlight=None):
        super().__init__(parent, height=height, bg=T["card"], highlightthickness=0)
        self.labels, self.values, self.kind = labels, values, kind
        self.highlight = highlight
        self.geo = None
        self.bind("<Configure>", lambda e: self.draw())
        self.bind("<Motion>", self._on_move)
        self.bind("<Leave>", lambda e: self.delete("tip"))

    def draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 60 or h < 60 or not self.values:
            return

        n = len(self.values)
        left, right, top = 58, 10, 12
        slot = (w - left - right) / n
        rotate = slot < 34
        bottom = 40 if rotate else 28
        pw, ph = w - left - right, h - top - bottom

        ticks = nice_ticks(max(self.values))
        vmax = ticks[-1]
        self.geo = (left, top, slot, ph, vmax)

        for t in ticks:
            y = top + ph - (t / vmax) * ph
            self.create_line(left, y, w - right, y, fill=T["border"], dash=(3, 3))
            self.create_text(left - 8, y, text=fmt(t), anchor="e",
                             fill=T["muted"], font=(UI_FONT, 8))

        pts = []
        for i, v in enumerate(self.values):
            cx = left + slot * i + slot / 2
            y = top + ph - (v / vmax) * ph

            if self.kind == "bar":
                half = min(slot * 0.30, 12)
                color = T["warn"] if i == self.highlight else T["brand"]
                self.create_rectangle(cx - half, y, cx + half, top + ph,
                                      fill=color, outline="")
            else:
                pts.append((cx, y))

            if rotate:
                self.create_text(cx, top + ph + 8, text=self.labels[i], anchor="ne",
                                 angle=45, fill=T["muted"], font=(UI_FONT, 8))
            else:
                self.create_text(cx, top + ph + 8, text=self.labels[i], anchor="n",
                                 fill=T["muted"], font=(UI_FONT, 8))

        if self.kind == "line" and pts:
            base = top + ph
            area = [pts[0][0], base] + [c for p in pts for c in p] + [pts[-1][0], base]
            self.create_polygon(*area, fill=T["brand_50"], outline="")
            if len(pts) > 1:
                self.create_line(*[c for p in pts for c in p],
                                 fill=T["brand"], width=2.5)
            for x, y in pts:
                self.create_oval(x - 3.5, y - 3.5, x + 3.5, y + 3.5,
                                 fill=T["card"], outline=T["brand"], width=2)

        self.create_line(left, top + ph, w - right, top + ph, fill=T["gray300"])

    def _on_move(self, event):
        self.delete("tip")
        if not self.geo:
            return
        left, top, slot, ph, vmax = self.geo
        i = int((event.x - left) // slot)
        if not 0 <= i < len(self.values):
            return

        v = self.values[i]
        cx = left + slot * i + slot / 2
        y = top + ph - (v / vmax) * ph
        text = f"{self.labels[i]}  ·  {fmt(v)}"
        tw = len(text) * 6.2 + 16
        x0 = min(max(cx - tw / 2, 4), self.winfo_width() - tw - 4)
        y0 = max(y - 34, 2)

        self.create_rectangle(x0, y0, x0 + tw, y0 + 24, fill=T["text"],
                              outline="", tags="tip")
        self.create_text(x0 + tw / 2, y0 + 12, text=text, fill="white",
                         font=(UI_FONT, 9, "bold"), tags="tip")


# =================================================================
# PAGE
# =================================================================

class WifiDashboard:

    def __init__(self, root, on_close=None, repository=None):

        self.root = root
        self.on_close = on_close
        self.repository = repository  # branchez ici votre source réelle

        self.root.title("Rapport quotidien — revenus YAS WiFi")
        self.root.configure(fg_color=T["bg"]) if hasattr(self.root, "configure") else None

        self._fonts()
        self.build_interface()
        self.refresh()

    # -------------------------------------------------------------
    # DONNEES (démo) — remplacer par votre table de revenus
    # -------------------------------------------------------------

    def get_report_data(self):

        if self.repository is not None and hasattr(self.repository, "get_wifi_report"):
            return self.repository.get_wifi_report()

        days = ["21/09", "22/09", "23/09", "24/09", "25/09", "26/09", "27/09",
                "28/09", "29/09", "30/09", "01/10", "02/10", "03/10", "04/10",
                "05/10", "06/10", "07/10"]
        revenue = [3000, 105000, 97000, 90000, 98000, 100000, 94000, 88000,
                   103000, 88000, 82000, 90000, 83000, 90000, 102000, 94000, 80500]
        numbers = [12, 420, 385, 355, 392, 400, 375, 352, 410, 352, 328,
                   358, 332, 355, 408, 376, 322]

        cumul, run = [], 0
        for v in revenue:
            run += v
            cumul.append(run)

        total = run
        total_numbers = sum(numbers)
        last = revenue[-1]
        avg7 = sum(revenue[-8:-1]) / 7
        variation = (last - avg7) / avg7 * 100
        med = median(revenue)
        low = [i for i, v in enumerate(revenue) if v < 0.2 * med]
        threshold = 30

        checks = [
            ("Données de la veille présentes (retard en jours)", "0", "0", True),
            ("Aucun jour manquant (nombre de jours)", "0", "0", True),
            ("Aucun doublon de jour (nombre)", "0", "0", True),
            ("Nbre Numéro × prix = revenu (nombre d'écarts)", "0", "0", True),
            ("Prix unitaire conforme (Numéros hors prix attendu)", "0", "0", True),
            ("Aucune valeur vide ou négative (nombre)", "0", "0", True),
            ("Revenu de la veille cohérent vs moyenne 7 jours",
             f"{variation:+.1f}%".replace(".", ","), f"±{threshold}%",
             abs(variation) <= threshold),
        ]

        # zones de recharge : (nom, lon, lat, part)
        raw = [("Lomé", 1.22, 6.13, 0.38), ("Kara", 1.19, 9.55, 0.12),
               ("Sokodé", 1.13, 8.98, 0.11), ("Kpalimé", 0.63, 6.90, 0.08),
               ("Atakpamé", 1.13, 7.53, 0.07), ("Aného", 1.60, 6.23, 0.06),
               ("Tsévié", 1.21, 6.43, 0.06), ("Dapaong", 0.20, 10.86, 0.05),
               ("Mango", 0.47, 10.36, 0.03), ("Bassar", 0.78, 9.25, 0.02)]
        s = sum(r[3] for r in raw)
        zones = [{
            "name": n, "lon": lo, "lat": la, "share": p / s,
            "amount": total * p / s, "recharges": round(total_numbers * p / s),
        } for n, lo, la, p in raw]

        # points de détail par ville (quartiers) pour le zoom de la carte
        for z in zones:
            z["spots"] = make_spots(z)

        return {
            "days": days, "revenue": revenue, "numbers": numbers, "cumul": cumul,
            "total": total, "total_numbers": total_numbers,
            "avg_day": total / len(days), "avg_numbers": total_numbers / len(days),
            "last": last, "last_numbers": numbers[-1],
            "variation": variation, "threshold": threshold,
            "checks": checks, "median": med,
            "first_day": "21/09/2026", "last_day": "07/10/2026",
            "checked_day": "07/10/2026",
            "low_count": len(low),
            "low_day": "21/09/2026" if low else "—",
            "low_lines": 9 if low else 0,
            "low_revenue": revenue[low[0]] if low else 0,
            "low_idx": low[0] if low else None,
            "zones": zones,
        }

    # -------------------------------------------------------------
    # POLICES
    # -------------------------------------------------------------

    def _fonts(self):
        global UI_FONT
        try:
            if "Outfit" in tkfont.families(self.root):
                UI_FONT = "Outfit"
        except Exception:
            pass

        F = lambda size, weight="normal", **kw: ctk.CTkFont(
            family=UI_FONT, size=size, weight=weight, **kw)

        self.f_title = F(22, "bold")
        self.f_sub = F(11)
        self.f_btn = F(12, "bold")
        self.f_card_title = F(16, "bold")
        self.f_card_sub = F(11)
        self.f_kpi_label = F(12)
        self.f_kpi_value = F(26, "bold")
        self.f_head = F(11, "bold")
        self.f_cell = F(12)
        self.f_cell_bold = F(12, "bold")
        self.f_alert_title = F(14, "bold")
        self.f_alert_sub = F(12)
        self.f_zone = F(12, "bold")
        self.f_zone_sub = F(10)

    # -------------------------------------------------------------
    # SQUELETTE
    # -------------------------------------------------------------

    def build_interface(self):

        outer = ctk.CTkFrame(self.root, fg_color=T["bg"], corner_radius=0)
        outer.pack(fill="both", expand=True)

        self.topbar = ctk.CTkFrame(outer, fg_color=T["bg"], corner_radius=0)
        self.topbar.pack(fill="x", padx=30, pady=(20, 14))

        self.body = ctk.CTkScrollableFrame(
            outer, fg_color=T["bg"], corner_radius=0,
            scrollbar_button_color=T["gray300"],
            scrollbar_button_hover_color=T["muted"]
        )
        self.body.pack(fill="both", expand=True, padx=(30, 20), pady=(0, 16))

    def refresh(self):

        self.data = self.get_report_data()

        for frame in (self.topbar, self.body):
            for w in frame.winfo_children():
                w.destroy()

        self.build_topbar()
        self.build_alert(self.body)
        self.build_kpis(self.body)
        self.build_main(self.body)
        self.build_tables(self.body)

    def close_window(self):
        if self.on_close:
            self.on_close()
        else:
            self.root.destroy()

    # -------------------------------------------------------------
    # EN-TETE + BOUTON RETOUR
    # -------------------------------------------------------------

    def build_topbar(self):

        ctk.CTkButton(
            self.topbar, text="  Retour", font=self.f_btn,
            image=icon("arrow_left", T["text_soft"], 16), compound="left",
            fg_color=T["card"], hover_color=T["gray100"], text_color=T["text_soft"],
            border_width=1, border_color=T["gray300"], corner_radius=10,
            height=40, width=110, command=self.close_window
        ).pack(side="left", padx=(0, 20))

        titles = ctk.CTkFrame(self.topbar, fg_color="transparent")
        titles.pack(side="left")

        ctk.CTkLabel(
            titles, text="Rapport quotidien : revenus YAS WiFi",
            font=self.f_title, text_color=T["text"], fg_color="transparent"
        ).pack(anchor="w")

        ctk.CTkLabel(
            titles,
            text="Source : table des revenus YAS WiFi · le contrôle porte sur "
                 "la veille de la date de contrôle",
            font=self.f_sub, text_color=T["muted"], fg_color="transparent"
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(
            self.topbar, text="  Actualiser", font=self.f_btn,
            image=icon("refresh", "#FFFFFF", 16), compound="left",
            fg_color=T["brand"], hover_color=T["brand_dark"], text_color="#FFFFFF",
            corner_radius=10, height=40, width=130, command=self.refresh
        ).pack(side="right")

        make_pill(
            self.topbar, f"Contrôle du {self.data['checked_day']}",
            T["text_soft"], T["gray100"], height=32, size=11
        ).pack(side="right", padx=(0, 12))

    # -------------------------------------------------------------
    # ALERTE GLOBALE (style TailAdmin "Alert")
    # -------------------------------------------------------------

    def build_alert(self, parent):

        checks = self.data["checks"]
        failed = sum(1 for *_, ok in checks if not ok)
        ok = failed == 0

        fg, soft, border, strong = (
            (T["ok"], T["ok_50"], T["ok_200"], T["ok_text"]) if ok
            else (T["err"], T["err_50"], T["err_200"], T["err_text"])
        )

        box = ctk.CTkFrame(parent, fg_color=soft, corner_radius=14,
                           border_width=1, border_color=border)
        box.pack(fill="x", pady=(0, 16))

        badge = ctk.CTkFrame(box, fg_color=fg, width=40, height=40, corner_radius=20)
        badge.pack(side="left", padx=(18, 14), pady=16)
        badge.pack_propagate(False)
        ctk.CTkLabel(
            badge, text="✓" if ok else "!", text_color="#FFFFFF",
            font=ctk.CTkFont(family=UI_FONT, size=18, weight="bold"),
            fg_color="transparent"
        ).pack(expand=True)

        texts = ctk.CTkFrame(box, fg_color="transparent")
        texts.pack(side="left", pady=14)

        ctk.CTkLabel(
            texts,
            text="Tous les contrôles sont OK" if ok
            else f"{failed} contrôle(s) en échec",
            font=self.f_alert_title, text_color=strong, fg_color="transparent"
        ).pack(anchor="w")
        ctk.CTkLabel(
            texts, text=f"{len(checks)} contrôles exécutés · {failed} en échec",
            font=self.f_alert_sub, text_color=T["text_soft"], fg_color="transparent"
        ).pack(anchor="w")

    # -------------------------------------------------------------
    # KPI
    # -------------------------------------------------------------

    def build_kpis(self, parent):

        d = self.data
        var = d["variation"]
        var_txt = f"{abs(var):.1f} %".replace(".", ",")
        within = abs(var) <= d["threshold"]

        var_fg, var_bg = (
            (T["ok_text"], T["ok_50"]) if var >= 0 else (T["err_text"], T["err_50"])
        )

        kpis = [
            ("chart", "Revenu total (FCFA)", fmt(d["total"]),
             f"moy. {fmt(d['avg_day'])} / jour", T["text_soft"], T["gray100"]),
            ("list", "Numéros vendus", fmt(d["total_numbers"]),
             f"moy. {fmt(d['avg_numbers'])} / jour", T["text_soft"], T["gray100"]),
            ("check_circle", "Revenu de la veille (FCFA)", fmt(d["last"]),
             f"{'↑' if var >= 0 else '↓'} {var_txt}", var_fg, var_bg),
            ("warning" if not within else "layers", "Variation vs moyenne 7 jours",
             f"{'+' if var >= 0 else '−'}{var_txt}",
             f"seuil ±{d['threshold']} %",
             T["ok_text"] if within else T["err_text"],
             T["ok_50"] if within else T["err_50"]),
        ]

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 16))
        for i in range(4):
            row.grid_columnconfigure(i, weight=1, uniform="kpi")

        for i, (ic, label, value, pill, pfg, pbg) in enumerate(kpis):
            c = make_card(row)
            c.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))

            top = ctk.CTkFrame(c, fg_color="transparent")
            top.pack(fill="x", padx=20, pady=(20, 0))

            box = ctk.CTkFrame(top, fg_color=T["gray100"], width=48, height=48,
                               corner_radius=12)
            box.pack(side="left")
            box.pack_propagate(False)
            ctk.CTkLabel(box, text="", image=icon(ic, T["text_soft"], 22),
                         fg_color="transparent").pack(expand=True)

            make_pill(top, f"  {pill}  ", pfg, pbg).pack(side="right", anchor="n")

            ctk.CTkLabel(c, text=label, font=self.f_kpi_label,
                         text_color=T["muted"], fg_color="transparent"
                         ).pack(anchor="w", padx=20, pady=(16, 0))
            ctk.CTkLabel(c, text=value, font=self.f_kpi_value,
                         text_color=T["text"], fg_color="transparent"
                         ).pack(anchor="w", padx=20, pady=(2, 20))

    # -------------------------------------------------------------
    # ZONE PRINCIPALE : graphiques (2/3) + carte du Togo (1/3)
    # -------------------------------------------------------------

    def _chart_card(self, parent, title, subtitle, **chart_kw):

        c = make_card(parent)
        ctk.CTkLabel(c, text=title, font=self.f_card_title, text_color=T["text"],
                     fg_color="transparent").pack(anchor="w", padx=20, pady=(18, 0))
        ctk.CTkLabel(c, text=subtitle, font=self.f_card_sub, text_color=T["muted"],
                     fg_color="transparent").pack(anchor="w", padx=20, pady=(0, 6))
        Chart(c, self.data["days"], **chart_kw).pack(
            fill="both", expand=True, padx=14, pady=(0, 14))
        return c

    def build_main(self, parent):

        d = self.data

        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="x", pady=(0, 16))
        wrap.grid_columnconfigure(0, weight=2, uniform="main")
        wrap.grid_columnconfigure(1, weight=1, uniform="main")

        # ---- colonne gauche : 3 graphiques ----
        left = ctk.CTkFrame(wrap, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self._chart_card(
            left, "Revenu par jour", "FCFA · en orange : jour anormalement bas",
            values=d["revenue"], kind="bar", highlight=d["low_idx"]
        ).pack(fill="x", pady=(0, 12))

        self._chart_card(
            left, "Numéros — souscriptions par jour", "Nombre de numéros vendus",
            values=d["numbers"], kind="bar"
        ).pack(fill="x", pady=(0, 12))

        self._chart_card(
            left, "Revenu cumulé", "FCFA · depuis le premier jour chargé",
            values=d["cumul"], kind="line"
        ).pack(fill="x")

        # ---- colonne droite : carte ----
        right = make_card(wrap)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(right, text="Zones de recharge", font=self.f_card_title,
                     text_color=T["text"], fg_color="transparent"
                     ).pack(anchor="w", padx=20, pady=(18, 0))
        ctk.CTkLabel(right,
                     text="Molette pour zoomer · glisser pour déplacer · "
                          "zoomez sur une ville pour voir ses points",
                     font=self.f_card_sub, text_color=T["muted"],
                     fg_color="transparent", wraplength=380, justify="left"
                     ).pack(anchor="w", padx=20, pady=(0, 8))

        mapframe = ctk.CTkFrame(right, fg_color=T["card"], corner_radius=12,
                                border_width=1, border_color=T["border"])
        mapframe.pack(fill="x", padx=16)
        TogoMap(mapframe, d["zones"], height=430, font=UI_FONT,
                scroll_parent=self.body).pack(fill="both", expand=True,
                                              padx=6, pady=6)

        ctk.CTkFrame(right, height=1, fg_color=T["border"]).pack(
            fill="x", padx=20, pady=(14, 4))

        for z in sorted(d["zones"], key=lambda z: -z["share"])[:6]:
            self._zone_row(right, z)

        ctk.CTkFrame(right, fg_color="transparent", height=10).pack()

    def _zone_row(self, parent, z):

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=6)

        av = ctk.CTkFrame(row, fg_color=T["brand_50"], width=36, height=36,
                          corner_radius=18)
        av.pack(side="left", padx=(0, 10))
        av.pack_propagate(False)
        ctk.CTkLabel(av, text=z["name"][0], text_color=T["brand"],
                     font=self.f_zone, fg_color="transparent").pack(expand=True)

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left")
        ctk.CTkLabel(info, text=z["name"], font=self.f_zone,
                     text_color=T["text"], fg_color="transparent").pack(anchor="w")
        ctk.CTkLabel(info, text=f"{fmt(z['recharges'])} recharges",
                     font=self.f_zone_sub, text_color=T["muted"],
                     fg_color="transparent").pack(anchor="w")

        pct = ctk.CTkLabel(row, text=f"{z['share'] * 100:.0f}%", font=self.f_zone,
                           text_color=T["text_soft"], fg_color="transparent", width=36)
        pct.pack(side="right")

        bar = ctk.CTkProgressBar(row, width=90, height=7, corner_radius=4,
                                 fg_color=T["gray100"], progress_color=T["brand"])
        bar.set(z["share"])
        bar.pack(side="right", padx=(0, 8))

    # -------------------------------------------------------------
    # TABLEAUX (style "Recent Orders")
    # -------------------------------------------------------------

    def _table(self, parent, column, title, subtitle, headers, aligns, rows,
               minsizes, expand_col=0):

        shell = make_card(parent)
        shell.grid(row=0, column=column, sticky="nsew",
                   padx=(0, 8) if column == 0 else (8, 0))

        ctk.CTkLabel(shell, text=title, font=self.f_card_title, text_color=T["text"],
                     fg_color="transparent").pack(anchor="w", padx=20, pady=(18, 0))
        ctk.CTkLabel(shell, text=subtitle, font=self.f_card_sub, text_color=T["muted"],
                     fg_color="transparent").pack(anchor="w", padx=20, pady=(0, 12))

        grid = ctk.CTkFrame(shell, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=(0, 16))

        ncol = len(headers)
        for c in range(ncol):
            grid.grid_columnconfigure(c, weight=1 if c == expand_col else 0,
                                      minsize=minsizes[c])

        def divider(r):
            ctk.CTkFrame(grid, height=1, fg_color=T["border"]).grid(
                row=r, column=0, columnspan=ncol, sticky="ew")

        divider(0)
        for c, h in enumerate(headers):
            ctk.CTkLabel(
                grid, text=h, font=self.f_head, text_color=T["muted"],
                fg_color=T["gray50"], anchor=aligns[c], height=34, corner_radius=0
            ).grid(row=1, column=c, sticky="nsew",
                   padx=(10, 0) if aligns[c] == "w" else (0, 10) if aligns[c] == "e" else 0)
        divider(2)

        r = 3
        for row in rows:
            bg = row.get("bg") or "transparent"
            for c, cell in enumerate(row["cells"]):
                self._put_cell(grid, r, c, cell, aligns[c], bg)
            divider(r + 1)
            r += 2

    def _put_cell(self, grid, r, c, cell, align, bg):

        pad = (10, 0) if align == "w" else (0, 10) if align == "e" else 0

        if isinstance(cell, dict) and "pill" in cell:
            holder = ctk.CTkFrame(grid, fg_color=bg, corner_radius=0, height=40)
            holder.grid(row=r, column=c, sticky="nsew")
            ok = cell["ok"]
            make_pill(
                holder, cell["pill"],
                T["ok_text"] if ok else T["err_text"],
                T["ok_50"] if ok else T["err_50"], width=54
            ).place(relx=0.5, rely=0.5, anchor="center")
            return

        text, bold, muted = (
            (cell, False, False) if isinstance(cell, str)
            else (cell["text"], cell.get("bold", False), cell.get("muted", False))
        )
        ctk.CTkLabel(
            grid, text=text, anchor=align, height=40, corner_radius=0,
            font=self.f_cell_bold if bold else self.f_cell,
            text_color=T["muted"] if muted else T["text"] if bold else T["text_soft"],
            fg_color=bg
        ).grid(row=r, column=c, sticky="nsew", padx=pad)

    def build_tables(self, parent):

        d = self.data

        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="x", pady=(0, 10))
        wrap.grid_columnconfigure(0, weight=1, uniform="tbl")
        wrap.grid_columnconfigure(1, weight=1, uniform="tbl")

        # ---- Contrôles du jour ----
        failed = sum(1 for *_, ok in d["checks"] if not ok)
        rows = [
            {"cells": [str(i), name, {"text": val, "bold": True}, exp,
                       {"pill": "OK" if ok else "KO", "ok": ok}]}
            for i, (name, val, exp, ok) in enumerate(d["checks"], start=1)
        ]
        rows.append({
            "bg": T["gray50"],
            "cells": ["", {"text": "Contrôles en échec", "bold": True}, "", "",
                      {"pill": str(failed), "ok": failed == 0}],
        })

        self._table(
            wrap, 0, "Contrôles du jour", "Résultat des 7 contrôles d'intégrité",
            ["N°", "Contrôle", "Valeur", "Attendu", "Statut"],
            ["center", "w", "center", "center", "center"],
            rows, [44, 0, 70, 70, 80], expand_col=1
        )

        # ---- Repères ----
        def warn(label, value, indent=False):
            return {"bg": T["warn_50"], "cells": [
                {"text": ("      ↳ " if indent else "") + label,
                 "bold": not indent},
                {"text": value, "bold": True}]}

        rows = [
            {"cells": ["Premier jour chargé", {"text": d["first_day"], "bold": True}]},
            {"cells": ["Dernier jour chargé", {"text": d["last_day"], "bold": True}]},
            {"cells": ["Jour contrôlé (veille de la date de contrôle)",
                       {"text": d["checked_day"], "bold": True}]},
            {"cells": ["Médiane journalière (FCFA)",
                       {"text": fmt(d["median"]), "bold": True}]},
            warn("Jours anormalement bas (< seuil × médiane)", str(d["low_count"])),
            warn("Premier jour concerné", d["low_day"], True),
            warn("Lignes ce jour-là", str(d["low_lines"]), True),
            warn("Revenu ce jour-là (FCFA)", fmt(d["low_revenue"]), True),
        ]

        self._table(
            wrap, 1, "Repères et points d'attention",
            "Informatif — hors statut des contrôles",
            ["Indicateur", "Valeur"], ["w", "e"], rows, [0, 130], expand_col=0
        )


# =================================================================
# TEST AUTONOME
# =================================================================

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    app = ctk.CTk()
    app.geometry("1360x900")
    app.minsize(1200, 750)
    WifiDashboard(app)
    app.mainloop()