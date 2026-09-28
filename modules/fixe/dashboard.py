import tkinter as tk
from tkinter import messagebox
from datetime import datetime

import customtkinter as ctk

from config import APP_TITLE, APP_WIDTH, APP_HEIGHT, DEMO_MODE
from services.dashboard_service import DashboardService
from services.demo_data import DemoRepository
from ui.detail_modal import DetailModal
from ui.icons import icon
from ui.palette import COLORS, FONT, MONO, SEVERITY_COLORS


FAMILIES = {
    "Population": "Population et complétude",
    "Exactitude": "Exactitude du calcul",
    "Charges spécifiques": "Charges spécifiques",
    "Revue qualitative": "Revue qualitative",
}

NAV_ITEMS = [
    ("dashboard", "Dashboard", "home"),
    ("catalogue", "Catalogue", "list"),
    ("categories", "Catégories", "layers"),
    ("resumes", "Résumés", "chart"),
    ("details", "Détails", "search"),
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
        self.f_brand = ctk.CTkFont(family=FONT, size=15, weight="bold")
        self.f_brand_sub = ctk.CTkFont(family=FONT, size=10)
        self.f_group = ctk.CTkFont(family=FONT, size=10, weight="bold")
        self.f_nav = ctk.CTkFont(family=FONT, size=12, weight="bold")
        self.f_nav_back = ctk.CTkFont(family=FONT, size=12)
        self.f_title = ctk.CTkFont(family=FONT, size=24, weight="bold")
        self.f_subtitle = ctk.CTkFont(family=FONT, size=11)
        self.f_meta = ctk.CTkFont(family=MONO, size=9)
        self.f_kpi_label = ctk.CTkFont(family=FONT, size=11)
        self.f_kpi_value = ctk.CTkFont(family=FONT, size=28, weight="bold")
        self.f_label = ctk.CTkFont(family=FONT, size=11, weight="bold")
        self.f_pill = ctk.CTkFont(family=FONT, size=11, weight="bold")
        self.f_section = ctk.CTkFont(family=FONT, size=16, weight="bold")
        self.f_section_count = ctk.CTkFont(family=FONT, size=11)
        self.f_card_id = ctk.CTkFont(family=MONO, size=9)
        self.f_card_badge = ctk.CTkFont(family=FONT, size=9, weight="bold")
        self.f_card_name = ctk.CTkFont(family=FONT, size=12, weight="bold")
        self.f_card_value = ctk.CTkFont(family=FONT, size=22, weight="bold")
        self.f_card_caption = ctk.CTkFont(family=FONT, size=9)

    # =============================================================
    # INTERFACE GENERALE
    # =============================================================

    def build_interface(self):

        outer = ctk.CTkFrame(self.root, fg_color=COLORS["bg"], corner_radius=0)
        outer.pack(fill="both", expand=True)

        self.build_sidebar(outer)

        main_area = ctk.CTkFrame(outer, fg_color=COLORS["bg"], corner_radius=0)
        main_area.pack(side="left", fill="both", expand=True)

        # ---- Zone FIXE : en-tête, KPI, filtres (ne défile jamais) ----
        self.fixed = ctk.CTkFrame(main_area, fg_color=COLORS["bg"], corner_radius=0)
        self.fixed.pack(fill="x", padx=30, pady=(20, 0))

        self.build_header(self.fixed)
        self.build_statistics(self.fixed)
        self.build_toolbar(self.fixed)

        # ---- Zone SCROLLABLE : uniquement la liste des contrôles ----
        self.sections = ctk.CTkScrollableFrame(
            main_area, fg_color=COLORS["bg"], corner_radius=0,
            scrollbar_button_color=COLORS["track"],
            scrollbar_button_hover_color=COLORS["muted"]
        )
        self.sections.pack(fill="both", expand=True, padx=(30, 20), pady=(0, 16))

    # =============================================================
    # SIDEBAR
    # =============================================================

    def build_sidebar(self, parent):

        sidebar = ctk.CTkFrame(
            parent, fg_color=COLORS["panel"], width=250, corner_radius=0
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkFrame(parent, fg_color=COLORS["border"], width=1, corner_radius=0).pack(
            side="left", fill="y"
        )

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=24, pady=(26, 26))

        ctk.CTkLabel(
            brand, text="", image=icon("logo", COLORS["accent"], 36),
            fg_color="transparent"
        ).pack(side="left", padx=(0, 12))

        titles = ctk.CTkFrame(brand, fg_color="transparent")
        titles.pack(side="left")

        ctk.CTkLabel(
            titles, text="BillingFixControl", font=self.f_brand,
            text_color=COLORS["text"], fg_color="transparent"
        ).pack(anchor="w")

        ctk.CTkLabel(
            titles, text="Revenue Assurance", font=self.f_brand_sub,
            text_color=COLORS["muted"], fg_color="transparent"
        ).pack(anchor="w")

        ctk.CTkLabel(
            sidebar, text="MENU", font=self.f_group,
            text_color=COLORS["muted"], fg_color="transparent"
        ).pack(anchor="w", padx=28, pady=(0, 10))

        nav_container = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_container.pack(fill="x", padx=14)

        self.nav_frames = {}
        self.active_nav = "dashboard"

        for key, label, icon_name in NAV_ITEMS:
            self.build_nav_item(nav_container, key, label, icon_name)

        self.update_nav_highlight()

        bottom = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=14, pady=20)

        ctk.CTkButton(
            bottom, text="  Retour à l'accueil", font=self.f_nav_back,
            image=icon("arrow_left", COLORS["muted"], 16), compound="left",
            fg_color="transparent", text_color=COLORS["muted"],
            hover_color=COLORS["panel_2"], anchor="w", height=40, corner_radius=10,
            command=self.close_window
        ).pack(fill="x")

    def build_nav_item(self, parent, key, label, icon_name):

        row = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=10, height=44)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12)

        icon_lbl = ctk.CTkLabel(
            inner, text="", image=icon(icon_name, COLORS["muted"], 20),
            width=24, fg_color="transparent"
        )
        icon_lbl.pack(side="left", padx=(2, 10))

        text_lbl = ctk.CTkLabel(
            inner, text=label, font=self.f_nav,
            text_color=COLORS["text_soft"], fg_color="transparent", anchor="w"
        )
        text_lbl.pack(side="left", fill="x", expand=True)

        self.nav_frames[key] = {
            "row": row, "icon": icon_lbl, "text": text_lbl, "icon_name": icon_name
        }

        def click(event=None, k=key):
            self.on_nav_click(k)

        def enter(event=None, k=key):
            if k != self.active_nav:
                row.configure(fg_color=COLORS["panel_2"])

        def leave(event=None, k=key):
            if k != self.active_nav:
                row.configure(fg_color="transparent")

        for widget in (row, inner, icon_lbl, text_lbl):
            widget.bind("<Button-1>", click)
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)
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
            refs["row"].configure(
                fg_color=COLORS["accent_soft"] if active else "transparent"
            )
            refs["icon"].configure(
                image=icon(refs["icon_name"],
                           COLORS["accent"] if active else COLORS["muted"], 20)
            )
            refs["text"].configure(
                text_color=COLORS["accent"] if active else COLORS["text_soft"]
            )

    def close_window(self):
        self.root.destroy()

    # =============================================================
    # HEADER
    # =============================================================

    def build_header(self, parent):

        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 18))

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
            right, text="  Actualiser", font=self.f_pill, command=self.refresh,
            image=icon("refresh", COLORS["white"], 16), compound="left",
            fg_color=COLORS["accent"], hover_color=COLORS["accent_dark"],
            text_color=COLORS["white"], corner_radius=10, height=38, width=140
        ).pack(anchor="e", pady=(10, 0))

    # =============================================================
    # STATISTIQUES (KPI)
    # =============================================================

    def build_statistics(self, parent):

        self.stats = ctk.CTkFrame(parent, fg_color="transparent")
        self.stats.pack(fill="x", pady=(0, 16))

        for i in range(4):
            self.stats.grid_columnconfigure(i, weight=1, uniform="kpi")

    def render_stats(self):

        for widget in self.stats.winfo_children():
            widget.destroy()

        counts = self.service.counters(self.cards)

        values = [
            (counts["total"], "Contrôles suivis", COLORS["accent"],
             COLORS["accent_soft"], "list"),
            (counts["critical"], "En statut critique", COLORS["critical"],
             COLORS["critical_bg"], "alert"),
            (counts["attention"], "En attention", COLORS["attention"],
             COLORS["attention_bg"], "warning"),
            (counts["ok"], "Sans anomalie", COLORS["ok"],
             COLORS["ok_bg"], "check_circle"),
        ]

        for i, (value, title, color, soft, icon_name) in enumerate(values):

            card = ctk.CTkFrame(
                self.stats, fg_color=COLORS["panel"], corner_radius=16,
                border_width=1, border_color=COLORS["border"]
            )
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))

            box = ctk.CTkFrame(
                card, fg_color=soft, width=46, height=46, corner_radius=12
            )
            box.pack(side="left", padx=(20, 14), pady=18)
            box.pack_propagate(False)

            ctk.CTkLabel(
                box, text="", image=icon(icon_name, color, 22),
                fg_color="transparent"
            ).pack(expand=True)

            texts = ctk.CTkFrame(card, fg_color="transparent")
            texts.pack(side="left", fill="x", expand=True, pady=14)

            ctk.CTkLabel(
                texts, text=title, font=self.f_kpi_label,
                text_color=COLORS["muted"], fg_color="transparent"
            ).pack(anchor="w")

            ctk.CTkLabel(
                texts, text=str(value), font=self.f_kpi_value,
                text_color=COLORS["text"], fg_color="transparent"
            ).pack(anchor="w")

    # =============================================================
    # TOOLBAR (Date / Perimetre / Mode / Familles)
    # =============================================================

    def _segmented(self, parent, values, variable, command):

        return ctk.CTkSegmentedButton(
            parent, values=values, variable=variable, command=command,
            font=self.f_pill, corner_radius=10, height=36, border_width=3,
            fg_color=COLORS["track"], selected_color=COLORS["panel"],
            selected_hover_color=COLORS["panel"],
            unselected_color=COLORS["track"],
            unselected_hover_color=COLORS["border"],
            text_color=COLORS["text"]
        )

    def build_toolbar(self, parent):

        toolbar = ctk.CTkFrame(
            parent, fg_color=COLORS["panel"], corner_radius=16,
            border_width=1, border_color=COLORS["border"]
        )
        toolbar.pack(fill="x", pady=(0, 10))

        row1 = ctk.CTkFrame(toolbar, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=(16, 12))

        # ---- Date + Charger ----
        ctk.CTkLabel(
            row1, text="Date d'exécution", font=self.f_label,
            text_color=COLORS["muted"], fg_color="transparent"
        ).pack(side="left", padx=(0, 8))

        self.date_entry = ctk.CTkEntry(
            row1, textvariable=self.date_var, width=130, height=36,
            placeholder_text="AAAA-MM-JJ", corner_radius=10,
            fg_color=COLORS["panel"], border_color=COLORS["border"],
            text_color=COLORS["text"], placeholder_text_color=COLORS["muted"]
        )
        self.date_entry.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            row1, text="Charger", font=self.f_pill, command=self.load_selected_date,
            fg_color=COLORS["panel_2"], hover_color=COLORS["track"],
            text_color=COLORS["text"], corner_radius=10, height=36, width=90
        ).pack(side="left", padx=(0, 28))

        # ---- Perimetre ----
        ctk.CTkLabel(
            row1, text="Périmètre", font=self.f_label,
            text_color=COLORS["muted"], fg_color="transparent"
        ).pack(side="left", padx=(0, 10))

        self.perimetre_selector = self._segmented(
            row1, ["Toutes", "FXL", "HYB"],
            self.perimetre_var, lambda v: self.on_filter_changed()
        )
        self.perimetre_selector.pack(side="left", padx=(0, 28))

        # ---- Mode d'execution ----
        ctk.CTkLabel(
            row1, text="Mode", font=self.f_label,
            text_color=COLORS["muted"], fg_color="transparent"
        ).pack(side="left", padx=(0, 10))

        self.mode_selector = self._segmented(
            row1, ["COMMIT", "SIMULATION"],
            self.mode_var, lambda v: self.on_filter_changed()
        )
        self.mode_selector.pack(side="left")

        # ---- Séparateur ----
        ctk.CTkFrame(toolbar, fg_color=COLORS["border"], height=1).pack(fill="x", padx=20)

        # ---- Familles (2e ligne) ----
        row2 = ctk.CTkFrame(toolbar, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(12, 16))

        family_values = ["Toutes les familles"] + list(FAMILIES.values())

        self.family_selector = self._segmented(
            row2, family_values, self.family_var, lambda v: self.render_cards()
        )
        self.family_selector.pack(side="left")

    # =============================================================
    # CHARGEMENT
    # =============================================================

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
    # CARTES (zone scrollable)
    # =============================================================

    def render_cards(self):

        for widget in self.sections.winfo_children():
            widget.destroy()

        selected = self.family_var.get()
        displayed = 0

        for family, display_name in FAMILIES.items():

            if selected != "Toutes les familles" and selected != display_name:
                continue

            cards = [c for c in self.cards if c.famille == family]

            if not cards:
                continue

            displayed += 1

            title_row = ctk.CTkFrame(self.sections, fg_color="transparent")
            title_row.pack(fill="x", pady=(8, 8))

            ctk.CTkLabel(
                title_row, text=display_name, font=self.f_section,
                text_color=COLORS["text"], fg_color="transparent"
            ).pack(side="left")

            ctk.CTkLabel(
                title_row, text=f"{len(cards)} contrôle{'s' if len(cards) > 1 else ''}",
                font=self.f_section_count, text_color=COLORS["muted"],
                fg_color="transparent"
            ).pack(side="left", padx=(10, 0), pady=(3, 0))

            grid = ctk.CTkFrame(self.sections, fg_color="transparent")
            grid.pack(fill="x", pady=(0, 10))

            for column in range(4):
                grid.grid_columnconfigure(column, weight=1, uniform="control")

            for index, card in enumerate(cards):
                widget = self.build_control_card(grid, card)
                widget.grid(row=index // 4, column=index % 4, sticky="nsew", padx=5, pady=5)

        if displayed == 0:
            ctk.CTkLabel(
                self.sections, text="Aucun contrôle pour les filtres sélectionnés.",
                font=self.f_subtitle, text_color=COLORS["muted"], fg_color="transparent"
            ).pack(pady=50)

    def build_control_card(self, parent, card):

        severite = card.severite or "N/A"
        color, bg = SEVERITY_COLORS.get(severite, SEVERITY_COLORS["N/A"])

        frame = ctk.CTkFrame(
            parent, fg_color=COLORS["panel"], corner_radius=16,
            border_width=1, border_color=COLORS["border"], cursor="hand2"
        )

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(16, 0))

        ctk.CTkLabel(
            top, text=f"CTRL-{card.control_id:02d}", font=self.f_card_id,
            text_color=COLORS["muted"], fg_color="transparent"
        ).pack(side="left")

        ctk.CTkLabel(
            top, text=f"  {severite}  ", font=self.f_card_badge,
            text_color=color, fg_color=bg, corner_radius=11, height=22
        ).pack(side="right")

        ctk.CTkLabel(
            frame, text=card.control_name, font=self.f_card_name,
            text_color=COLORS["text"], fg_color="transparent",
            anchor="w", justify="left", wraplength=200
        ).pack(fill="x", padx=18, pady=(12, 14))

        ctk.CTkFrame(frame, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=18)

        bottom = ctk.CTkFrame(frame, fg_color="transparent")
        bottom.pack(fill="x", padx=18, pady=(12, 16))

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

        # ---- Interactions : clic + survol sur toute la carte ----

        def click(event=None, c=card):
            self.open_detail(c)

        def enter(event=None):
            frame.configure(border_color=COLORS["accent"])

        def leave(event=None):
            try:
                x, y = frame.winfo_pointerxy()
                under = frame.winfo_containing(x, y)
                if under is not None and str(under).startswith(str(frame)):
                    return
            except Exception:
                pass
            frame.configure(border_color=COLORS["border"])

        def bind_recursive(widget):
            widget.bind("<Button-1>", click)
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)
            try:
                widget.configure(cursor="hand2")
            except Exception:
                pass
            for child in widget.winfo_children():
                bind_recursive(child)

        bind_recursive(frame)

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