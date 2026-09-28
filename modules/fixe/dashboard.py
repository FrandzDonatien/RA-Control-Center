import tkinter as tk
from tkinter import messagebox
from datetime import datetime

import customtkinter as ctk

from config import COLORS, APP_TITLE, APP_WIDTH, APP_HEIGHT, DEMO_MODE
from services.dashboard_service import DashboardService
from services.demo_data import DemoRepository
from ui.detail_modal import DetailModal


FAMILIES = {
    "Population": "Population et complétude",
    "Exactitude": "Exactitude du calcul",
    "Charges spécifiques": "Charges spécifiques",
    "Revue qualitative": "Revue qualitative",
}

SEVERITY_COLORS = {
    "CRITIQUE": (COLORS["critical"], COLORS.get("critical_bg", COLORS["panel_2"])),
    "ATTENTION": (COLORS["attention"], COLORS.get("attention_bg", COLORS["panel_2"])),
    "OK": (COLORS["ok"], COLORS.get("ok_bg", COLORS["panel_2"])),
    "N/A": (COLORS["muted"], COLORS["panel_2"]),
}

NAV_ITEMS = [
    ("dashboard", "Dashboard", "🏠"),
    ("catalogue", "Catalogue", "☰"),
    ("categories", "Catégories", "🗂"),
    ("resumes", "Résumés", "📊"),
    ("details", "Détails", "🔍"),
]


class Dashboard:

    def __init__(self, root, perimetre="FXL", mode_execution="COMMIT"):

        self.root = root

        self.root.title(APP_TITLE)
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.minsize(1200, 750)
        self.root.configure(fg_color=COLORS["bg"]) if hasattr(self.root, "configure") else None

        self.perimetre_var = tk.StringVar(value=perimetre)
        self.mode_var = tk.StringVar(value=mode_execution)
        self.family_var = tk.StringVar(value="Toutes les familles")
        self.date_var = tk.StringVar(value="")

        # ---------------------------------------------------------
        # Repository
        # ---------------------------------------------------------

        if DEMO_MODE:
            self.repository = DemoRepository()
            self.demo = True
        else:
            from repositories.control_repository import ControlRepository
            self.repository = ControlRepository()
            self.demo = False

        self.service = DashboardService(self.repository)

        self.cards = []
        self.selected_date = None
        self.stat_widgets = {}

        self._fonts()
        self.build_interface()
        self.refresh()

    # =============================================================
    # POLICES
    # =============================================================

    def _fonts(self):
        self.f_brand = ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        self.f_brand_sub = ctk.CTkFont(family="Segoe UI", size=10)
        self.f_nav = ctk.CTkFont(family="Segoe UI", size=12)
        self.f_title = ctk.CTkFont(family="Georgia", size=24, weight="bold")
        self.f_subtitle = ctk.CTkFont(family="Segoe UI", size=11)
        self.f_meta = ctk.CTkFont(family="Consolas", size=9)
        self.f_kpi_label = ctk.CTkFont(family="Segoe UI", size=11)
        self.f_kpi_value = ctk.CTkFont(family="Consolas", size=26, weight="bold")
        self.f_label = ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
        self.f_pill = ctk.CTkFont(family="Segoe UI", size=10, weight="bold")
        self.f_section = ctk.CTkFont(family="Georgia", size=15, weight="bold")
        self.f_card_id = ctk.CTkFont(family="Consolas", size=9)
        self.f_card_badge = ctk.CTkFont(family="Segoe UI", size=9, weight="bold")
        self.f_card_name = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        self.f_card_value = ctk.CTkFont(family="Consolas", size=20, weight="bold")
        self.f_card_caption = ctk.CTkFont(family="Segoe UI", size=9)

    # =============================================================
    # INTERFACE GENERALE
    # =============================================================

    def build_interface(self):

        outer = ctk.CTkFrame(self.root, fg_color=COLORS["bg"], corner_radius=0)
        outer.pack(fill="both", expand=True)

        self.build_sidebar(outer)

        main_area = ctk.CTkFrame(outer, fg_color=COLORS["bg"], corner_radius=0)
        main_area.pack(side="left", fill="both", expand=True)

        # Zone scrollable native CustomTkinter -- remplace le systeme
        # Canvas+Scrollbar manuel
        self.scroll = ctk.CTkScrollableFrame(
            main_area, fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["muted"]
        )
        self.scroll.pack(fill="both", expand=True, padx=30, pady=(20, 20))

        self.build_header()
        self.build_statistics()
        self.build_toolbar()

        self.sections = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.sections.pack(fill="both", expand=True, pady=(10, 30))

    # =============================================================
    # SIDEBAR
    # =============================================================

    def build_sidebar(self, parent):

        sidebar = ctk.CTkFrame(
            parent, fg_color=COLORS["panel"], width=250, corner_radius=0,
            border_width=0
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=24, pady=(26, 20))

        ctk.CTkLabel(
            brand, text="BillingFixControl", font=self.f_brand,
            text_color=COLORS["text"], fg_color="transparent"
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand, text="Revenue Assurance", font=self.f_brand_sub,
            text_color=COLORS["muted"], fg_color="transparent"
        ).pack(anchor="w")

        nav_container = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_container.pack(fill="x", padx=14)

        self.nav_frames = {}
        self.active_nav = "dashboard"

        for key, label, icon in NAV_ITEMS:
            self.build_nav_item(nav_container, key, label, icon)

        self.update_nav_highlight()

        bottom = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=14, pady=20)

        ctk.CTkButton(
            bottom, text="←  Retour à l'accueil", font=self.f_nav,
            fg_color="transparent", text_color=COLORS["muted"],
            hover_color=COLORS["panel_2"], anchor="w",
            command=self.close_window
        ).pack(fill="x")

    def build_nav_item(self, parent, key, label, icon):

        row = ctk.CTkFrame(parent, fg_color=COLORS["panel"], corner_radius=10, height=42)
        row.pack(fill="x", pady=3)
        row.pack_propagate(False)

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12)

        icon_lbl = ctk.CTkLabel(
            inner, text=icon, font=self.f_nav, width=22,
            text_color=COLORS["accent"], fg_color="transparent"
        )
        icon_lbl.pack(side="left", pady=9)

        text_lbl = ctk.CTkLabel(
            inner, text=label, font=self.f_nav,
            text_color=COLORS["text"], fg_color="transparent", anchor="w"
        )
        text_lbl.pack(side="left", fill="x", expand=True, pady=9)

        self.nav_frames[key] = {"row": row, "icon": icon_lbl, "text": text_lbl}

        def click(event=None, k=key):
            self.on_nav_click(k)

        for widget in (row, inner, icon_lbl, text_lbl):
            widget.bind("<Button-1>", click)
            widget.configure(cursor="hand2")

    def on_nav_click(self, key):

        self.active_nav = key
        self.update_nav_highlight()

        if key != "dashboard":
            messagebox.showinfo(
                "Module à venir",
                "Cette section n'est pas encore disponible.",
                parent=self.root
            )

    def update_nav_highlight(self):

        for key, refs in self.nav_frames.items():
            active = (key == self.active_nav)
            bg = COLORS.get("accent_soft", "#e7effa") if active else COLORS["panel"]
            refs["row"].configure(fg_color=bg)
            refs["icon"].configure(fg_color="transparent")
            refs["text"].configure(
                fg_color="transparent",
                text_color=COLORS["accent"] if active else COLORS["text"]
            )

    def close_window(self):
        self.root.destroy()

    # =============================================================
    # HEADER
    # =============================================================

    def build_header(self):

        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")

        ctk.CTkLabel(
            left, text="Registre des contrôles", font=self.f_title,
            text_color=COLORS["text"], fg_color="transparent"
        ).pack(anchor="w")

        ctk.CTkLabel(
            left, text="Revenue Assurance — Facturation postpaid", font=self.f_subtitle,
            text_color=COLORS["muted"], fg_color="transparent"
        ).pack(anchor="w", pady=(4, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right", anchor="n")

        self.meta = ctk.CTkLabel(
            right, text="", justify="right", font=self.f_meta,
            text_color=COLORS["muted"], fg_color="transparent"
        )
        self.meta.pack(anchor="e")

        ctk.CTkButton(
            right, text="↻ Actualiser", font=self.f_pill, command=self.refresh,
            fg_color=COLORS["accent"], hover_color=COLORS["accent"],
            text_color=COLORS["white"], corner_radius=18, height=34, width=130
        ).pack(anchor="e", pady=(10, 0))

    # =============================================================
    # STATISTIQUES (KPI avec barre de couleur)
    # =============================================================

    def build_statistics(self):

        self.stats = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.stats.pack(fill="x", pady=(0, 20))

        for i in range(4):
            self.stats.grid_columnconfigure(i, weight=1)

    def render_stats(self):

        for widget in self.stats.winfo_children():
            widget.destroy()

        counts = self.service.counters(self.cards)

        values = [
            (counts["total"], "Contrôles suivis", COLORS["accent"]),
            (counts["critical"], "En statut critique", COLORS["critical"]),
            (counts["attention"], "En attention", COLORS["attention"]),
            (counts["ok"], "Sans anomalie", COLORS["ok"]),
        ]

        for i, (value, title, color) in enumerate(values):

            card = ctk.CTkFrame(
                self.stats, fg_color=COLORS["panel"], corner_radius=14,
                border_width=1, border_color=COLORS["border"]
            )
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))

            ctk.CTkLabel(
                card, text=title, font=self.f_kpi_label,
                text_color=COLORS["muted"], fg_color="transparent"
            ).pack(anchor="w", padx=18, pady=(16, 4))

            ctk.CTkLabel(
                card, text=str(value), font=self.f_kpi_value,
                text_color=COLORS["text"], fg_color="transparent"
            ).pack(anchor="w", padx=18, pady=(0, 10))

            ctk.CTkFrame(
                card, fg_color=color, height=3, corner_radius=2
            ).pack(fill="x", padx=18, pady=(0, 16))

    # =============================================================
    # TOOLBAR (Date / Perimetre / Mode / Familles)
    # =============================================================

    def build_toolbar(self):

        row1 = ctk.CTkFrame(self.scroll, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 14))

        # ---- Date + Charger ----
        ctk.CTkLabel(
            row1, text="Exécution :", font=self.f_label,
            text_color=COLORS["muted"], fg_color="transparent"
        ).pack(side="left", padx=(0, 8))

        self.date_entry = ctk.CTkEntry(
            row1, textvariable=self.date_var, width=130, height=34,
            placeholder_text="AAAA-MM-JJ", corner_radius=17,
            fg_color=COLORS["panel_2"], border_color=COLORS["border"],
            text_color=COLORS["text"]
        )
        self.date_entry.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            row1, text="Charger", font=self.f_pill, command=self.load_selected_date,
            fg_color=COLORS["panel_2"], hover_color=COLORS["border"],
            text_color=COLORS["text"], corner_radius=17, height=34, width=90
        ).pack(side="left", padx=(0, 24))

        # ---- Perimetre ----
        ctk.CTkLabel(
            row1, text="Périmètre", font=self.f_label,
            text_color=COLORS["text"], fg_color="transparent"
        ).pack(side="left", padx=(0, 10))

        self.perimetre_selector = ctk.CTkSegmentedButton(
            row1, values=["Toutes", "FXL", "HYB"],
            variable=self.perimetre_var, command=lambda v: self.on_filter_changed(),
            font=self.f_pill, corner_radius=17, height=34,
            fg_color=COLORS["panel_2"], selected_color=COLORS["accent"],
            selected_hover_color=COLORS["accent"], unselected_color=COLORS["panel_2"],
            unselected_hover_color=COLORS["border"], text_color=COLORS["text"],
        )
        self.perimetre_selector.pack(side="left", padx=(0, 24))

        # ---- Mode d'execution ----
        ctk.CTkLabel(
            row1, text="Exécution", font=self.f_label,
            text_color=COLORS["text"], fg_color="transparent"
        ).pack(side="left", padx=(0, 10))

        self.mode_selector = ctk.CTkSegmentedButton(
            row1, values=["COMMIT", "SIMULATION"],
            variable=self.mode_var, command=lambda v: self.on_filter_changed(),
            font=self.f_pill, corner_radius=17, height=34,
            fg_color=COLORS["panel_2"], selected_color=COLORS["accent"],
            selected_hover_color=COLORS["accent"], unselected_color=COLORS["panel_2"],
            unselected_hover_color=COLORS["border"], text_color=COLORS["text"],
        )
        self.mode_selector.pack(side="left")

        # ---- Familles (2e ligne) ----
        row2 = ctk.CTkFrame(self.scroll, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))

        family_values = ["Toutes les familles"] + list(FAMILIES.values())

        self.family_selector = ctk.CTkSegmentedButton(
            row2, values=family_values,
            variable=self.family_var, command=lambda v: self.render_cards(),
            font=self.f_pill, corner_radius=17, height=34,
            fg_color=COLORS["panel_2"], selected_color=COLORS["accent"],
            selected_hover_color=COLORS["accent"], unselected_color=COLORS["panel_2"],
            unselected_hover_color=COLORS["border"], text_color=COLORS["text"],
        )
        self.family_selector.pack(side="left")

    # =============================================================
    # CHARGEMENT (logique inchangee)
    # =============================================================

    def refreshOld(self):

        try:
            latest = self.repository.get_latest_date()
            self.selected_date = latest

            if latest:
                self.date_var.set(latest.strftime("%Y-%m-%d"))

            self.load_cards()

        except Exception as exc:
            messagebox.showerror("Erreur", f"Impossible de charger les données.\n\n{exc}")

    def refresh(self):

        try:
            latest = self.repository.get_latest_date(
                self.perimetre_var.get(),
                self.mode_var.get()
            )
            self.selected_date = latest

            if latest:
                self.date_var.set(latest.strftime("%Y-%m-%d"))

            self.load_cards()

        except Exception as exc:
            messagebox.showerror("Erreur", f"Impossible de charger les données.\n\n{exc}")

    def load_selected_date(self):

        try:
            value = self.date_var.get().strip()

            if not value:
                self.refresh()
                return

            selected = datetime.strptime(value, "%Y-%m-%d").date()
            self.selected_date = selected
            self.load_cards()

        except ValueError:
            messagebox.showwarning("Date invalide", "Format attendu : YYYY-MM-DD")

    def load_cardsOld(self):

        self.cards = self.service.load_cards(self.selected_date)

        date_text = (
            self.selected_date.strftime("%d/%m/%Y")
            if self.selected_date else "—"
        )
        environment = "démo" if self.demo else "production"

        self.meta.configure(
            text=f"Dernière exécution : {date_text}\nEnvironnement : {environment}"
        )

        self.render_stats()
        self.render_cards()

    def load_cards(self):

        self.cards = self.service.load_cards(
            self.selected_date,
            self.perimetre_var.get(),
            self.mode_var.get()
        )

        date_text = (
            self.selected_date.strftime("%d/%m/%Y")
            if self.selected_date else "—"
        )
        environment = "démo" if self.demo else "production"

        self.meta.configure(
            text=(
                f"Dernière exécution : {date_text}\n"
                f"Environnement : {environment}\n"
                f"Périmètre : {self.perimetre_var.get()}\n"
                f"Mode : {self.mode_var.get()}"
            )
        )

        self.render_stats()
        self.render_cards()

    # =============================================================
    # CARTES
    # =============================================================

    def render_cards(self):

        for widget in self.sections.winfo_children():
            widget.destroy()

        selected = self.family_var.get()

        for family, display_name in FAMILIES.items():

            if selected != "Toutes les familles" and selected != display_name:
                continue

            cards = [c for c in self.cards if c.famille == family]

            if not cards:
                continue

            title_row = ctk.CTkFrame(self.sections, fg_color="transparent")
            title_row.pack(fill="x", pady=(14, 8))

            ctk.CTkLabel(
                title_row, text=display_name, font=self.f_section,
                text_color=COLORS["text"], fg_color="transparent"
            ).pack(side="left")

            grid = ctk.CTkFrame(self.sections, fg_color="transparent")
            grid.pack(fill="x", pady=(0, 10))

            for column in range(4):
                grid.grid_columnconfigure(column, weight=1, uniform="control")

            for index, card in enumerate(cards):
                widget = self.build_control_card(grid, card)
                widget.grid(row=index // 4, column=index % 4, sticky="nsew", padx=5, pady=5)

    def build_control_card(self, parent, card):

        severite = card.severite or "N/A"
        color, bg = SEVERITY_COLORS.get(severite, SEVERITY_COLORS["N/A"])

        frame = ctk.CTkFrame(
            parent, fg_color=COLORS["panel"], corner_radius=14,
            border_width=1, border_color=COLORS["border"], cursor="hand2"
        )

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(14, 0))

        ctk.CTkLabel(
            top, text=f"CTRL-{card.control_id:02d}", font=self.f_card_id,
            text_color=COLORS["muted"], fg_color="transparent"
        ).pack(side="left")

        badge = ctk.CTkLabel(
            top, text=severite, font=self.f_card_badge,
            text_color=color, fg_color=bg, corner_radius=10,
            width=1, height=20
        )
        badge.pack(side="right", ipadx=8)

        ctk.CTkLabel(
            frame, text=card.control_name, font=self.f_card_name,
            text_color=COLORS["text"], fg_color="transparent",
            anchor="w", justify="left", wraplength=200
        ).pack(fill="x", padx=16, pady=(10, 12))

        bottom = ctk.CTkFrame(frame, fg_color="transparent")
        bottom.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkLabel(
            bottom, text=str(card.nb_items), font=self.f_card_value,
            text_color=COLORS["text"], fg_color="transparent"
        ).pack(side="left")

        caption = ctk.CTkFrame(bottom, fg_color="transparent")
        caption.pack(side="right", anchor="s")

        ctk.CTkLabel(
            caption, text="éléments détectés", font=self.f_card_caption,
            text_color=COLORS["muted"], fg_color="transparent"
        ).pack(anchor="e")

        ctk.CTkLabel(
            caption, text=card.frequence, font=self.f_card_caption,
            text_color=COLORS["muted"], fg_color="transparent"
        ).pack(anchor="e")

        def click(event=None, c=card):
            self.open_detail(c)

        for widget in (frame, top, bottom):
            widget.bind("<Button-1>", click)

        return frame

    # =============================================================
    # DETAIL
    # =============================================================

    def open_detail(self, card):

        DetailModal(
            self.root,
            card,
            self.repository,
            self.perimetre_var.get(),
            self.mode_var.get()
        )

    # =============================================================
    # FILTRES
    # =============================================================

    def on_filter_changed(self):

        self.selected_date = None

        latest = self.repository.get_latest_date(
            self.perimetre_var.get(),
            self.mode_var.get()
        )

        self.selected_date = latest

        if latest:
            self.date_var.set(latest.strftime("%Y-%m-%d"))

        self.load_cards()