import tkinter as tk
from tkinter import ttk
import json

from config import COLORS
from ui.trend import TrendChart


class DetailModal(tk.Toplevel):

    def __init__(self, parent, card, repository, perimetre="FXL", mode_execution="COMMIT"):

        super().__init__(parent)

        self.card = card
        self.repository = repository
        self.perimetre = perimetre
        self.mode_execution = mode_execution

        self.title(
            f"CTRL-{card.control_id:02d} — "
            f"{card.control_name}"
        )

        self.configure(
            bg=COLORS["bg"]
        )

        self.geometry("1100x650")
        self.minsize(900, 550)

        self.transient(parent)
        self.grab_set()

        self.search_var = tk.StringVar()

        self.build()

        self.load_data()

    # =============================================================
    # BUILD
    # =============================================================

    def build(self):

        # =========================================================
        # HEADER
        # =========================================================

        header = tk.Frame(
            self,
            bg=COLORS["panel"]
        )

        header.pack(
            fill="x",
            padx=1,
            pady=1
        )

        left = tk.Frame(
            header,
            bg=COLORS["panel"]
        )

        left.pack(
            side="left",
            padx=20,
            pady=15
        )

        tk.Label(
            left,
            text=(
                f"CTRL-{self.card.control_id:02d} "
                f"— {self.card.control_name}"
            ),
            font=("Georgia", 17, "bold"),
            bg=COLORS["panel"],
            fg=COLORS["text"]
        ).pack(
            anchor="w"
        )

        tk.Label(
            left,
            text=self.card.description,
            font=("Segoe UI", 9),
            bg=COLORS["panel"],
            fg="#8f949e"
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        tk.Button(
            header,
            text="Fermer",
            command=self.destroy,
            bg=COLORS["panel"],
            fg="#bfc3ca",
            activebackground=COLORS["panel_2"],
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=6
        ).pack(
            side="right",
            padx=18
        )

        # =========================================================
        # SUMMARY
        # =========================================================

        summary = tk.Frame(
            self,
            bg=COLORS["bg"]
        )

        summary.pack(
            fill="x",
            padx=20,
            pady=(15, 10)
        )

        self.create_summary(
            summary,
            str(self.card.nb_items),
            "Éléments détectés"
        )

        self.create_summary(
            summary,
            self.card.severite,
            "Sévérité",
            self.card.severite
        )

        montant = (
            f"{self.card.montant_impacte:,.0f}"
            if self.card.montant_impacte is not None
            else "—"
        )

        self.create_summary(
            summary,
            montant,
            "Montant impacté"
        )

        self.create_summary(
            summary,
            self.card.frequence,
            "Fréquence"
        )

        # =========================================================
        # SEARCH
        # =========================================================

        search = tk.Frame(
            self,
            bg=COLORS["bg"]
        )

        search.pack(
            fill="x",
            padx=20,
            pady=(5, 8)
        )

        tk.Label(
            search,
            text="Recherche :",
            font=("Segoe UI", 9),
            bg=COLORS["bg"],
            fg="#777d88"
        ).pack(
            side="left",
            padx=(0, 8)
        )

        entry = tk.Entry(
            search,
            textvariable=self.search_var,
            width=35,
            font=("Segoe UI", 9),
            bg=COLORS["panel_2"],
            fg="#e4e5e8",
            insertbackground="white",
            relief="flat"
        )

        entry.pack(
            side="left",
            ipady=6
        )

        self.search_var.trace_add(
            "write",
            lambda *_: self.filter_rows()
        )

        # =========================================================
        # BODY
        # =========================================================

        body = tk.Frame(
            self,
            bg=COLORS["bg"]
        )

        body.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        # ---------------------------------------------------------
        # TABLE
        # ---------------------------------------------------------

        left = tk.Frame(
            body,
            bg=COLORS["panel"],
            highlightthickness=1,
            highlightbackground=COLORS["border"]
        )

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 7)
        )

        tk.Label(
            left,
            text="Éléments détectés — dernière exécution",
            font=("Segoe UI", 9),
            bg=COLORS["panel"],
            fg="#8f949e"
        ).pack(
            anchor="w",
            padx=14,
            pady=(12, 8)
        )

        tree_container = tk.Frame(
            left,
            bg=COLORS["panel"]
        )

        tree_container.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        self.tree = ttk.Treeview(
            tree_container,
            show="headings"
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = ttk.Scrollbar(
            tree_container,
            orient="vertical",
            command=self.tree.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        # ---------------------------------------------------------
        # TREND
        # ---------------------------------------------------------

        right = tk.Frame(
            body,
            bg=COLORS["panel"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            width=390
        )

        right.pack(
            side="right",
            fill="both",
            padx=(7, 0)
        )

        right.pack_propagate(False)

        tk.Label(
            right,
            text="Tendance — 7 dernières exécutions",
            font=("Segoe UI", 9),
            bg=COLORS["panel"],
            fg="#8f949e"
        ).pack(
            anchor="w",
            padx=14,
            pady=(12, 4)
        )

        self.chart = TrendChart(
            right,
            height=220
        )

        self.chart.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # =============================================================
    # SUMMARY CARD
    # =============================================================

    def create_summary(
        self,
        parent,
        value,
        label,
        status=None
    ):

        frame = tk.Frame(
            parent,
            bg=COLORS["panel"],
            highlightthickness=1,
            highlightbackground=COLORS["border"]
        )

        frame.pack(
            side="left",
            fill="x",
            expand=True,
            padx=2
        )

        color = COLORS["text"]

        if status == "CRITIQUE":
            color = COLORS["critical"]

        elif status == "ATTENTION":
            color = COLORS["attention"]

        elif status == "OK":
            color = COLORS["ok"]

        tk.Label(
            frame,
            text=value,
            font=("Segoe UI", 15, "bold"),
            bg=COLORS["panel"],
            fg=color
        ).pack(
            anchor="w",
            padx=12,
            pady=(10, 0)
        )

        tk.Label(
            frame,
            text=label,
            font=("Segoe UI", 8),
            bg=COLORS["panel"],
            fg="#777d88"
        ).pack(
            anchor="w",
            padx=12,
            pady=(0, 10)
        )

    # =============================================================
    # DATA
    # =============================================================

    def load_data(self):

        self.rows = self.repository.get_details(
            self.card.control_id,
            self.card.date_controle,
            self.perimetre,
            self.mode_execution
        )

        self.build_dynamic_columns()

        trend = self.repository.get_trend(
            self.card.control_id,
            self.card.date_controle,
            self.perimetre,
            self.mode_execution,
            7
        )

        # get_trend renvoie les dates du plus recent au plus ancien
        # (ORDER BY date_controle DESC) -- on remet dans l'ordre
        # chronologique pour que le graphique se lise de gauche a droite
        self.chart.redraw(list(reversed(trend)))

        self.filter_rows()

    # =============================================================
    # COLONNES DYNAMIQUES JSONB
    # =============================================================

    def build_dynamic_columns(self):

        columns = [
            "cle_metier",
            "categorie"
        ]

        for row in self.rows:

            detail = row.get("detail") or {}

            for key in detail.keys():

                if key not in columns:
                    columns.append(key)

        self.columns = columns

        self.tree["columns"] = columns

        for column in columns:

            self.tree.heading(
                column,
                text=column
            )

            if column == "cle_metier":
                width = 120

            elif column == "categorie":
                width = 160

            else:
                width = 130

            self.tree.column(
                column,
                width=width,
                minwidth=90
            )

    # =============================================================
    # AFFICHAGE
    # =============================================================

    def filter_rows(self):

        if not hasattr(self, "rows"):
            return

        search = (
            self.search_var
            .get()
            .strip()
            .lower()
        )

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in self.rows:

            detail = row.get("detail") or {}

            values = [
                row.get("cle_metier", ""),
                row.get("categorie", "")
            ]

            for column in self.columns[2:]:

                values.append(
                    detail.get(column, "")
                )

            searchable = " ".join(
                str(value)
                for value in values
            ).lower()

            if search and search not in searchable:
                continue

            self.tree.insert(
                "",
                "end",
                values=values
            )