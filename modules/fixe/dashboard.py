import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from config import COLORS, APP_TITLE, APP_WIDTH, APP_HEIGHT, DEMO_MODE
from services.dashboard_service import DashboardService
from services.demo_data import DemoRepository
from ui.widgets import StatCard, ControlCard
from ui.detail_modal import DetailModal


FAMILIES = {
    "Population": "Population et complétude",
    "Exactitude": "Exactitude du calcul",
    "Charges spécifiques": "Charges spécifiques",
    "Revue qualitative": "Revue qualitative",
}


class Dashboard:

    def __init__(self, root):

        self.root = root

        self.root.title(APP_TITLE)
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.minsize(1100, 700)
        self.root.configure(bg=COLORS["bg"])
        self.perimetre_var = tk.StringVar(value="FXL")

        self.mode_var = tk.StringVar(
            value="COMMIT"
        )

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

        self.family_var = tk.StringVar(
            value="Toutes les familles"
        )

        self.date_var = tk.StringVar(
            value=""
        )

        self.content = None

        self.build_interface()

        self.refresh()

    # =============================================================
    # INTERFACE
    # =============================================================

    def build_interface(self):

        container = tk.Frame(
            self.root,
            bg=COLORS["bg"]
        )

        container.pack(
            fill="both",
            expand=True
        )

        self.canvas = tk.Canvas(
            container,
            bg=COLORS["bg"],
            highlightthickness=0
        )

        scrollbar = tk.Scrollbar(
            container,
            orient="vertical",
            command=self.canvas.yview
        )

        self.content = tk.Frame(
            self.canvas,
            bg=COLORS["bg"]
        )

        self.content.bind(
            "<Configure>",
            lambda event:
            self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.content_window = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="n"
        )

        self.canvas.bind(
            "<Configure>",
            self.on_canvas_resize
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            self.on_mousewheel
        )

        self.build_header()

        self.build_separator()

        self.build_statistics()

        self.build_toolbar()

        self.sections = tk.Frame(
            self.content,
            bg=COLORS["bg"]
        )

        self.sections.pack(
            fill="both",
            padx=30,
            pady=(0, 50)
        )

    # =============================================================
    # HEADER
    # =============================================================

    def build_header(self):

        header = tk.Frame(
            self.content,
            bg=COLORS["bg"]
        )

        header.pack(
            fill="x",
            padx=30,
            pady=(38, 0)
        )

        left = tk.Frame(
            header,
            bg=COLORS["bg"]
        )

        left.pack(
            side="left"
        )

        tk.Label(
            left,
            text="Registre des contrôles",
            font=("Georgia", 28, "bold"),
            bg=COLORS["bg"],
            fg=COLORS["text"]
        ).pack(
            anchor="w"
        )

        tk.Label(
            left,
            text="Revenue Assurance — Facturation postpaid",
            font=("Segoe UI", 15),
            bg=COLORS["bg"],
            fg="#9297a1"
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        # ---------------------------------------------------------
        # Partie droite
        # ---------------------------------------------------------

        right = tk.Frame(
            header,
            bg=COLORS["bg"]
        )

        right.pack(
            side="right",
            anchor="n"
        )

        self.meta = tk.Label(
            right,
            text="",
            justify="right",
            font=("Consolas", 9),
            bg=COLORS["bg"],
            fg="#777d88"
        )

        self.meta.pack(
            anchor="e"
        )

        self.refresh_button = tk.Button(
            right,
            text="↻ Actualiser",
            command=self.refresh,
            font=("Segoe UI", 9),
            bg=COLORS["panel_2"],
            fg="#c7cbd2",
            activebackground=COLORS["border"],
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2"
        )

        self.refresh_button.pack(
            anchor="e",
            pady=(12, 0)
        )

    # =============================================================
    # SEPARATOR
    # =============================================================

    def build_separator(self):

        tk.Frame(
            self.content,
            bg="#c8c8c8",
            height=1
        ).pack(
            fill="x",
            padx=30,
            pady=(25, 18)
        )

    # =============================================================
    # STATISTIQUES
    # =============================================================

    def build_statistics(self):

        self.stats = tk.Frame(
            self.content,
            bg=COLORS["bg"]
        )

        self.stats.pack(
            fill="x",
            padx=30
        )

    def render_stats(self):

        for widget in self.stats.winfo_children():
            widget.destroy()

        counts = self.service.counters(
            self.cards
        )

        values = [
            (
                counts["total"],
                "Contrôles suivis",
                None
            ),
            (
                counts["critical"],
                "En statut critique",
                "CRITIQUE"
            ),
            (
                counts["attention"],
                "En attention",
                "ATTENTION"
            ),
            (
                counts["ok"],
                "Sans anomalie",
                "OK"
            )
        ]

        for value, title, status in values:

            card = StatCard(
                self.stats,
                value,
                title,
                status
            )

            card.pack(
                side="left",
                fill="x",
                expand=True,
                padx=(0, 1)
            )

    # =============================================================
    # TOOLBAR
    # =============================================================

    def build_toolbar(self):

        toolbar = tk.Frame(
            self.content,
            bg=COLORS["bg"]
        )

        toolbar.pack(
            fill="x",
            padx=30,
            pady=(30, 20)
        )

        # =========================================================
        # PERIMETRE
        # =========================================================

        scope_frame = tk.Frame(
            self.content,
            bg=COLORS["bg"]
        )

        scope_frame.pack(
            fill="x",
            padx=30,
            pady=(25, 5)
        )

        tk.Label(
            scope_frame,
            text="Périmètre",
            font=("Segoe UI", 13, "bold"),
            bg=COLORS["bg"],
            fg=COLORS["text"]
        ).pack(
            side="left",
            padx=(0, 12)
        )

        self.fxl_button = self.create_filter_button(
            scope_frame,
            "FXL",
            self.perimetre_var,
            "FXL",
            self.on_filter_changed
        )

        self.hyb_button = self.create_filter_button(
            scope_frame,
            "HYB",
            self.perimetre_var,
            "HYB",
            self.on_filter_changed
        )

        # =========================================================
        # MODE EXECUTION
        # =========================================================

        mode_frame = tk.Frame(
            self.content,
            bg=COLORS["bg"]
        )

        mode_frame.pack(
            fill="x",
            padx=30,
            pady=(5, 15)
        )

        tk.Label(
            mode_frame,
            text="Exécution",
            font=("Segoe UI", 13, "bold"),
            bg=COLORS["bg"],
            fg=COLORS["text"]
        ).pack(
            side="left",
            padx=(0, 12)
        )

        self.commit_button = self.create_filter_button(
            mode_frame,
            "●  COMMIT",
            self.mode_var,
            "COMMIT",
            self.on_filter_changed
        )

        self.simulation_button = self.create_filter_button(
            mode_frame,
            "SIMULATION",
            self.mode_var,
            "SIMULATION",
            self.on_filter_changed
        )

        # ---------------------------------------------------------
        # Date
        # ---------------------------------------------------------

        tk.Label(
            toolbar,
            text="Exécution :",
            font=("Segoe UI", 14),
            bg=COLORS["bg"],
            fg="#777d88"
        ).pack(
            side="left",
            padx=(0, 7)
        )

        self.date_entry = tk.Entry(
            toolbar,
            textvariable=self.date_var,
            width=13,
            font=("Consolas", 13),
            bg=COLORS["panel_2"],
            fg="#d9dce2",
            insertbackground="white",
            relief="flat"
        )

        self.date_entry.pack(
            side="left",
            padx=(0, 15),
            ipady=6
        )

        tk.Button(
            toolbar,
            text="Charger",
            command=self.load_selected_date,
            font=("Segoe UI", 9),
            bg=COLORS["panel_2"],
            fg="#c7cbd2",
            activebackground=COLORS["border"],
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=5
        ).pack(
            side="left",
            padx=(0, 20)
        )

        # ---------------------------------------------------------
        # Familles -- sur sa PROPRE ligne, sous le toolbar date/charger
        # (evite le debordement horizontal quand la fenetre est etroite)
        # ---------------------------------------------------------

        family_frame = tk.Frame(
            self.content,
            bg=COLORS["bg"]
        )

        family_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 15)
        )

        tk.Label(
            family_frame,
            text="Filtrer :",
            font=("Segoe UI", 14),
            bg=COLORS["bg"],
            fg="#777d88"
        ).pack(
            side="left",
            padx=(0, 8)
        )

        options = [
            ("Toutes les familles", "Toutes les familles")
        ]

        options += [
            (display, display)
            for display in FAMILIES.values()
        ]

        for text, value in options:

            tk.Radiobutton(
                family_frame,
                text=text,
                variable=self.family_var,
                value=value,
                command=self.render_cards,
                indicatoron=False,
                font=("Segoe UI", 14),
                bg=COLORS["panel_2"],
                fg="#899dcd",
                selectcolor=COLORS["muted"],
                activebackground=COLORS["ok"],
                activeforeground=COLORS["white"],
                relief="flat",
                padx=11,
                pady=6,
                cursor="hand2"
            ).pack(
                side="left",
                padx=(0, 5)
            )

    # =============================================================
    # CHARGEMENT
    # =============================================================

    def refreshOld(self):

        try:

            latest = self.repository.get_latest_date()

            self.selected_date = latest

            if latest:

                self.date_var.set(
                    latest.strftime("%Y-%m-%d")
                )

            self.load_cards()

        except Exception as exc:

            messagebox.showerror(
                "Erreur",
                f"Impossible de charger les données.\n\n{exc}"
            )

    def refresh(self):

        try:

            latest = self.repository.get_latest_date(
                self.perimetre_var.get(),
                self.mode_var.get()
            )

            self.selected_date = latest

            if latest:
                self.date_var.set(
                    latest.strftime("%Y-%m-%d")
                )

            self.load_cards()

        except Exception as exc:

            messagebox.showerror(
                "Erreur",
                f"Impossible de charger les données.\n\n{exc}"
            )

    def load_selected_date(self):

        try:

            value = self.date_var.get().strip()

            if not value:
                self.refresh()
                return

            selected = datetime.strptime(
                value,
                "%Y-%m-%d"
            ).date()

            self.selected_date = selected

            self.load_cards()

        except ValueError:

            messagebox.showwarning(
                "Date invalide",
                "Format attendu : YYYY-MM-DD"
            )

    def load_cardsOld(self):

        self.cards = self.service.load_cards(
            self.selected_date
        )

        date_text = (
            self.selected_date.strftime(
                "%d/%m/%Y"
            )
            if self.selected_date
            else "—"
        )

        environment = (
            "démo"
            if self.demo
            else "production"
        )

        self.meta.config(
            text=
            f"Dernière exécution : {date_text}\n"
            f"Environnement : {environment}"
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
            if self.selected_date
            else "—"
        )

        environment = (
            "démo"
            if self.demo
            else "production"
        )

        self.meta.config(
            text=(
                f"Dernière exécution : {date_text}\n"
                f"Environnement : {environment}\n"
                f"Périmètre : {self.perimetre_var.get()}\n"
                f"Mode : {self.mode_var.get()}"
            ),
            font=("Georgia", 14),
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

            if (
                selected != "Toutes les familles"
                and selected != display_name
            ):
                continue

            cards = [
                card
                for card in self.cards
                if card.famille == family
            ]

            if not cards:
                continue

            # -----------------------------------------------------
            # Titre famille
            # -----------------------------------------------------

            title = tk.Frame(
                self.sections,
                bg=COLORS["bg"]
            )

            title.pack(
                fill="x",
                pady=(12, 7)
            )

            tk.Label(
                title,
                text=display_name,
                font=("Georgia", 16, "bold"),
                bg=COLORS["bg"],
                fg=COLORS["text"]
            ).pack(
                side="left"
            )

            tk.Frame(
                title,
                bg=COLORS["border"],
                height=1
            ).pack(
                side="left",
                fill="x",
                expand=True,
                padx=(15, 0),
                pady=5
            )

            # -----------------------------------------------------
            # Grid
            # -----------------------------------------------------

            grid = tk.Frame(
                self.sections,
                bg=COLORS["bg"]
            )

            grid.pack(
                fill="x",
                pady=(0, 18)
            )

            for column in range(3):

                grid.grid_columnconfigure(
                    column,
                    weight=1,
                    uniform="control"
                )

            for index, card in enumerate(cards):

                widget = ControlCard(
                    grid,
                    card,
                    self.open_detail
                )

                widget.grid(
                    row=index // 3,
                    column=index % 3,
                    sticky="nsew",
                    padx=4,
                    pady=4
                )

    # =============================================================
    # DETAIL
    # =============================================================

    def open_detail(self, card):

        DetailModal(
            self.root,
            card,
            self.repository
        )

    # =============================================================
    # SCROLL
    # =============================================================

    def on_mousewheel(self, event):

        self.canvas.yview_scroll(
            int(-event.delta / 120),
            "units"
        )
    def create_filter_button(self,parent,text,variable,value,command):

        button = tk.Radiobutton(
            parent,

            text=text,

            variable=variable,

            value=value,

            indicatoron=False,

            font=("Segoe UI", 9, "bold"),

            bg=COLORS["panel_2"],

            fg="white",

            selectcolor=COLORS["accent"],

            activebackground=COLORS["accent"],

            activeforeground="white",

            relief="flat",

            bd=0,

            padx=18,

            pady=8,

            cursor="hand2",

            command=command
        )

        button.pack(
            side="left",
            padx=(0, 5)
        )

        return button


    def on_filter_changed(self):
        self.selected_date = None

        latest = self.repository.get_latest_date(
            self.perimetre_var.get(),
            self.mode_var.get()
        )

        self.selected_date = latest

        if latest:
            self.date_var.set(
                latest.strftime("%Y-%m-%d")
            )

        self.load_cards()

    def on_canvas_resize(self, event):

        canvas_width = event.width

        # Largeur maximale du dashboard
        max_width = 1650
        margin = 20  # px de marge totale (10px de chaque cote)

        content_width = max(canvas_width - margin, 400)

        self.canvas.itemconfigure(
            self.content_window,
            width=content_width
        )

        # Centrage horizontal
        self.canvas.coords(
            self.content_window,
            canvas_width / 2,
            0
        )