import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from .theme import COLORS

ctk.set_appearance_mode("light")
ctk.set_widget_scaling(1.0)


class ControlCenter(ctk.CTk):

    MODULES = [
        ("FIXE",          "Dashboard Postpaid / Fixe",       "▣", "fixe"),
        ("FTTH",          "Contrôles Fibre",                  "⌁", "ftth"),
        ("INTERCONNECT",  "Contrôles Interconnect",           "⇄", "interconnect"),
        ("SIMBOX",        "Contrôles SIMBOX",                 "▤", "simbox"),
        ("A2P / P2A",     "Messaging Revenue Assurance",      "✉", "a2p_p2a"),
        ("FRANCHISE",     "Contrôles Franchise",              "◆", "franchise"),
    ]

    def __init__(self):
        super().__init__()

        self.title("RA Control Center")
        self.geometry("1380x820")
        self.minsize(1120, 680)
        self.configure(fg_color=COLORS["bg"])

        self._fonts()
        self.build()

    # =================================================================
    # POLICES
    # =================================================================

    def _fonts(self):
        self.f_logo = ctk.CTkFont(family="Segoe UI", size=28, weight="bold")
        self.f_title = ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        self.f_subtitle = ctk.CTkFont(family="Segoe UI", size=9)
        self.f_section = ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        self.f_hint = ctk.CTkFont(family="Segoe UI", size=10)
        self.f_status = ctk.CTkFont(family="Segoe UI", size=9, weight="bold")
        self.f_card_icon = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        self.f_card_name = ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        self.f_card_desc = ctk.CTkFont(family="Segoe UI", size=9)
        self.f_card_cta = ctk.CTkFont(family="Segoe UI", size=9, weight="bold")
        self.f_footer = ctk.CTkFont(family="Segoe UI", size=8)

    # =================================================================
    # BUILD
    # =================================================================

    def build(self):

        # -------------------------------------------------------
        # HEADER
        # -------------------------------------------------------

        header = ctk.CTkFrame(self, fg_color=COLORS["bg"], height=92)
        header.pack(fill="x", padx=34, pady=(24, 0))
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="◈", font=self.f_logo,
            text_color=COLORS["accent"], fg_color="transparent"
        ).pack(side="left", padx=(0, 12))

        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.pack(side="left", pady=5)

        ctk.CTkLabel(
            titles, text="RA CONTROL CENTER", font=self.f_title,
            text_color=COLORS["text"], fg_color="transparent"
        ).pack(anchor="w")

        ctk.CTkLabel(
            titles, text="Revenue Assurance • Central Control", font=self.f_subtitle,
            text_color=COLORS["muted"], fg_color="transparent"
        ).pack(anchor="w")

        status = ctk.CTkFrame(
            header, fg_color=COLORS["panel"], corner_radius=18,
            border_width=1, border_color=COLORS["border"]
        )
        status.pack(side="right", pady=8)

        ctk.CTkLabel(
            status, text="●", text_color=COLORS["success"],
            fg_color="transparent"
        ).pack(side="left", padx=(16, 6), pady=10)

        ctk.CTkLabel(
            status, text="Système opérationnel", font=self.f_status,
            text_color=COLORS["text"], fg_color="transparent"
        ).pack(side="left", padx=(0, 16))

        # -------------------------------------------------------
        # BODY
        # -------------------------------------------------------

        body = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=34)

        ctk.CTkLabel(
            body, text="Modules Revenue Assurance", font=self.f_section,
            text_color=COLORS["text"], fg_color="transparent"
        ).pack(anchor="w", pady=(8, 5))

        ctk.CTkLabel(
            body, text="Sélectionnez un domaine pour ouvrir son environnement de contrôle.",
            font=self.f_hint, text_color=COLORS["muted"], fg_color="transparent"
        ).pack(anchor="w", pady=(0, 22))

        grid = ctk.CTkFrame(body, fg_color="transparent")
        grid.pack(fill="both", expand=True)

        for i, module in enumerate(self.MODULES):
            card = self.build_card(grid, module)
            card.grid(row=i // 3, column=i % 3, sticky="nsew", padx=8, pady=8)

        for c in range(3):
            grid.grid_columnconfigure(c, weight=1)
        for r in range(2):
            grid.grid_rowconfigure(r, weight=1)

        # -------------------------------------------------------
        # FOOTER
        # -------------------------------------------------------

        footer = ctk.CTkFrame(self, fg_color=COLORS["sidebar"], height=42, corner_radius=0)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        ctk.CTkLabel(
            footer, text="Revenue Assurance • RA Control Center", font=self.f_footer,
            text_color=COLORS["muted"], fg_color="transparent"
        ).pack(side="left", padx=25)

        ctk.CTkLabel(
            footer, text="v1.0", font=ctk.CTkFont(family="Consolas", size=8),
            text_color=COLORS["muted"], fg_color="transparent"
        ).pack(side="right", padx=25)

    # =================================================================
    # CARTE MODULE
    # =================================================================

    def build_card(self, parent, module):

        name, desc, icon, key = module

        card = ctk.CTkFrame(
            parent, fg_color=COLORS["panel"], corner_radius=16,
            border_width=1, border_color=COLORS["border"]
        )

        icon_box = ctk.CTkFrame(
            card, fg_color=COLORS["panel_2"], width=60, height=60,
            corner_radius=14
        )
        icon_box.pack(anchor="w", padx=22, pady=(24, 18))
        icon_box.pack_propagate(False)

        ctk.CTkLabel(
            icon_box, text=icon, font=self.f_card_icon,
            text_color=COLORS["accent"], fg_color="transparent"
        ).pack(expand=True)

        ctk.CTkLabel(
            card, text=name, font=self.f_card_name,
            text_color=COLORS["text"], fg_color="transparent"
        ).pack(anchor="w", padx=22)

        ctk.CTkLabel(
            card, text=desc, font=self.f_card_desc,
            text_color=COLORS["muted"], fg_color="transparent",
            wraplength=290, justify="left"
        ).pack(anchor="w", padx=22, pady=(7, 18))

        ctk.CTkFrame(card, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=22)

        cta = ctk.CTkFrame(card, fg_color="transparent")
        cta.pack(fill="x", padx=22, pady=16)

        ctk.CTkLabel(
            cta, text="Ouvrir le module", font=self.f_card_cta,
            text_color=COLORS["accent"], fg_color="transparent"
        ).pack(side="left")

        ctk.CTkLabel(
            cta, text="→", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS["accent"], fg_color="transparent"
        ).pack(side="right")

        # -----------------------------------------------------------
        # Interactions (clic + hover -- CTkFrame n'a pas ces
        # comportements integres comme CTkButton, on les recree)
        # -----------------------------------------------------------

        def click(event=None):
            self.open(key)

        def enter(event=None):
            card.configure(border_color=COLORS["accent"], border_width=2)

        def leave(event=None):
            card.configure(border_color=COLORS["border"], border_width=1)

        def bind_recursive(widget):
            widget.bind("<Button-1>", click)
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)
            widget.configure(cursor="hand2") if hasattr(widget, "configure") else None
            for child in widget.winfo_children():
                bind_recursive(child)

        bind_recursive(card)

        return card

    # =================================================================
    # OUVERTURE D'UN MODULE
    # =================================================================

    def open(self, key):

        if key != "fixe":
            messagebox.showinfo(
                key.upper(),
                f"Le module {key.upper()} sera ajouté prochainement.",
                parent=self
            )
            return

        try:
            from modules.fixe.dashboard import Dashboard
        except ImportError as e:
            messagebox.showerror(
                "Dashboard FIXE",
                "Impossible de charger le module FIXE.\n\n" + str(e),
                parent=self
            )
            return

        w = ctk.CTkToplevel(self)
        w.withdraw()  # cache la fenetre pendant sa construction, evite
                       # le flash noir connu de CTkToplevel sous Windows
        w.title("RA • FIXE")
        w.geometry("1500x950")
        w.minsize(1250, 800)
        w.configure(fg_color=COLORS["bg"])

        w.lift()
        w.focus_force()

        try:
            w.tk.call("tk", "scaling", 1.20)
        except Exception:
            pass

        try:
            Dashboard(w, perimetre="FXL", mode_execution="COMMIT")
        except TypeError:
            Dashboard(w)
        except Exception as e:
            w.destroy()
            messagebox.showerror("Erreur Dashboard FIXE", str(e), parent=self)
            return

        w.after(10, w.deiconify)  # affiche seulement une fois le contenu construit