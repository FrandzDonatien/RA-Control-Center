from tkinter import messagebox

import customtkinter as ctk
from PIL import Image, ImageDraw

ctk.set_appearance_mode("light")
ctk.set_widget_scaling(1.0)


# =====================================================================
# PALETTE (inspirée de TailAdmin)
# =====================================================================

PALETTE = {
    "bg":          "#F9FAFB",   # fond de page
    "surface":     "#FFFFFF",   # blanc TailAdmin (sidebar, header, cartes)
    "border":      "#E4E7EC",
    "text":        "#1D2939",
    "text_soft":   "#344054",
    "muted":       "#667085",
    "brand":       "#465FFF",
    "brand_soft":  "#ECF3FF",
    "hover":       "#F2F4F7",
    "success":     "#12B76A",
    "success_bg":  "#ECFDF3",
    "success_txt": "#027A48",
    "neutral_bg":  "#F2F4F7",
}

FONT = "Segoe UI"


# =====================================================================
# ICONES (dessinées avec Pillow, sans emoji ni police externe)
# =====================================================================

_ICON_CACHE = {}


def _draw_icon(name, color, size):
    """Dessine une icône 'outline' (grille 24x24) en haute résolution."""
    S = 16
    N = 24 * S
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w = int(1.9 * S)

    def P(*pts):
        return [(x * S, y * S) for x, y in pts]

    def line(*pts):
        d.line(P(*pts), fill=color, width=w, joint="curve")
        r = w / 2
        for x, y in P(*pts):          # extrémités arrondies
            d.ellipse((x - r, y - r, x + r, y + r), fill=color)

    def rrect(x0, y0, x1, y1, r=2.0):
        d.rounded_rectangle(
            (x0 * S, y0 * S, x1 * S, y1 * S), radius=r * S,
            outline=color, width=w
        )

    if name == "home":
        line((3, 11), (12, 3.5), (21, 11))
        line((5.5, 9.5), (5.5, 20), (18.5, 20), (18.5, 9.5))
        rrect(10, 14, 14, 20, 1)

    elif name == "chart":
        line((6, 20), (6, 12))
        line((12, 20), (12, 5))
        line((18, 20), (18, 9))

    elif name == "fiber":
        for r in (4.5, 8.5, 12.5):
            d.arc(P((12 - r, 19 - r), (12 + r, 19 + r)),
                  start=225, end=315, fill=color, width=w)
        d.ellipse(P((10.4, 17.4), (13.6, 20.6)), fill=color)

    elif name == "interconnect":
        line((4, 8), (20, 8))
        line((15.5, 3.5), (20, 8), (15.5, 12.5))
        line((20, 16), (4, 16))
        line((8.5, 11.5), (4, 16), (8.5, 20.5))

    elif name == "simbox":
        line((6, 3), (15, 3), (19, 7), (19, 21), (6, 21), (6, 3))
        rrect(9.5, 11, 15.5, 17, 1.2)

    elif name == "mail":
        rrect(3, 5, 21, 19, 2.5)
        line((3.8, 7), (12, 13), (20.2, 7))

    elif name == "store":
        rrect(3, 4, 21, 9.5, 1.5)
        line((5, 9.5), (5, 20), (19, 20), (19, 9.5))
        rrect(10, 14, 14, 20, 0.8)

    elif name == "arrow":
        line((5, 12), (19, 12))
        line((13, 6), (19, 12), (13, 18))

    elif name == "search":
        d.ellipse(P((4, 4), (17, 17)), outline=color, width=w)
        line((15.5, 15.5), (20, 20))

    elif name == "bell":
        d.arc(P((7, 3), (17, 13)), start=180, end=360, fill=color, width=w)
        line((7, 8), (5, 17), (19, 17), (17, 8))
        d.arc(P((9.5, 15), (14.5, 22)), start=0, end=180, fill=color, width=w)

    elif name == "logo":
        d.rounded_rectangle((0, 0, N - 1, N - 1), radius=6 * S, fill=color)
        d2 = (255, 255, 255, 255)
        pts = P((7, 12.5), (10.6, 16), (17, 8.5))
        d.line(pts, fill=d2, width=int(2.4 * S), joint="curve")
        for x, y in (pts[0], pts[-1]):
            r = 1.2 * S
            d.ellipse((x - r, y - r, x + r, y + r), fill=d2)

    return img.resize((size * 4, size * 4), Image.LANCZOS)


def icon(name, color, size=20):
    key = (name, color, size)
    if key not in _ICON_CACHE:
        img = _draw_icon(name, color, size)
        _ICON_CACHE[key] = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
    return _ICON_CACHE[key]


# =====================================================================
# FENETRE PRINCIPALE
# =====================================================================

class ControlCenter(ctk.CTk):
    # (nom, description, icône, clé)
    MODULES = [
        ("FIXE",         "Dashboard Postpaid / Fixe",   "chart",        "fixe"),
        ("FTTH",         "Contrôles Fibre",             "fiber",        "ftth"),
        ("INTERCONNECT", "Contrôles Interconnect",      "interconnect", "interconnect"),
        ("SIMBOX",       "Contrôles SIMBOX",            "simbox",       "simbox"),
        ("A2P / P2A",    "Messaging Revenue Assurance", "mail",         "a2p_p2a"),
        ("FRANCHISE",    "Contrôles Franchise",         "store",        "franchise"),
    ]

    AVAILABLE = {"fixe"}

    def __init__(self):
        super().__init__()

        self.title("RA Control Center")
        self.geometry("1380x820")
        self.minsize(1120, 680)
        self.configure(fg_color=PALETTE["bg"])

        self.search_var = ctk.StringVar(value="")
        self.nav_items = {}

        self._fonts()
        self.build()

    # =================================================================
    # POLICES
    # =================================================================

    def _fonts(self):
        self.f_brand = ctk.CTkFont(family=FONT, size=17, weight="bold")
        self.f_brand_sub = ctk.CTkFont(family=FONT, size=10)
        self.f_group = ctk.CTkFont(family=FONT, size=10, weight="bold")
        self.f_nav = ctk.CTkFont(family=FONT, size=12, weight="bold")
        self.f_page = ctk.CTkFont(family=FONT, size=24, weight="bold")
        self.f_hint = ctk.CTkFont(family=FONT, size=11)
        self.f_search = ctk.CTkFont(family=FONT, size=12)
        self.f_status = ctk.CTkFont(family=FONT, size=10, weight="bold")
        self.f_avatar = ctk.CTkFont(family=FONT, size=11, weight="bold")
        self.f_card_name = ctk.CTkFont(family=FONT, size=16, weight="bold")
        self.f_card_desc = ctk.CTkFont(family=FONT, size=11)
        self.f_card_cta = ctk.CTkFont(family=FONT, size=11, weight="bold")
        self.f_badge = ctk.CTkFont(family=FONT, size=9, weight="bold")
        self.f_footer = ctk.CTkFont(family=FONT, size=9)

    # =================================================================
    # BUILD
    # =================================================================

    def build(self):

        self.build_sidebar()

        right = ctk.CTkFrame(self, fg_color=PALETTE["bg"], corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        self.build_header(right)
        self.build_footer(right)
        self.build_body(right)

    # =================================================================
    # SIDEBAR
    # =================================================================

    def build_sidebar(self):

        sidebar = ctk.CTkFrame(
            self, fg_color=PALETTE["surface"], width=272, corner_radius=0
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # séparateur droit
        ctk.CTkFrame(self, fg_color=PALETTE["border"], width=1, corner_radius=0).pack(
            side="left", fill="y"
        )

        # ---- Marque ----
        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=24, pady=(26, 28))

        ctk.CTkLabel(
            brand, text="", image=icon("logo", PALETTE["brand"], 38),
            fg_color="transparent"
        ).pack(side="left", padx=(0, 12))

        titles = ctk.CTkFrame(brand, fg_color="transparent")
        titles.pack(side="left")

        ctk.CTkLabel(
            titles, text="RA Control Center", font=self.f_brand,
            text_color=PALETTE["text"], fg_color="transparent"
        ).pack(anchor="w")

        ctk.CTkLabel(
            titles, text="Revenue Assurance", font=self.f_brand_sub,
            text_color=PALETTE["muted"], fg_color="transparent"
        ).pack(anchor="w")

        # ---- Navigation ----
        ctk.CTkLabel(
            sidebar, text="MENU", font=self.f_group,
            text_color=PALETTE["muted"], fg_color="transparent"
        ).pack(anchor="w", padx=28, pady=(0, 10))

        nav = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav.pack(fill="x", padx=16)

        self.build_nav_item(nav, "home", "Accueil", "home", active=True)

        ctk.CTkLabel(
            sidebar, text="MODULES", font=self.f_group,
            text_color=PALETTE["muted"], fg_color="transparent"
        ).pack(anchor="w", padx=28, pady=(22, 10))

        nav2 = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav2.pack(fill="x", padx=16)

        for name, _desc, icon_name, key in self.MODULES:
            self.build_nav_item(nav2, key, name, icon_name)

        # ---- Bas de sidebar ----
        ctk.CTkLabel(
            sidebar, text="v1.0", font=self.f_footer,
            text_color=PALETTE["muted"], fg_color="transparent"
        ).pack(side="bottom", anchor="w", padx=28, pady=20)

    def build_nav_item(self, parent, key, label, icon_name, active=False):

        row = ctk.CTkFrame(
            parent, height=44, corner_radius=10,
            fg_color=PALETTE["brand_soft"] if active else "transparent"
        )
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)

        color = PALETTE["brand"] if active else PALETTE["muted"]

        ico = ctk.CTkLabel(
            row, text="", image=icon(icon_name, color, 20),
            fg_color="transparent", width=24
        )
        ico.pack(side="left", padx=(14, 10))

        txt = ctk.CTkLabel(
            row, text=label, font=self.f_nav, anchor="w",
            text_color=PALETTE["brand"] if active else PALETTE["text_soft"],
            fg_color="transparent"
        )
        txt.pack(side="left", fill="x", expand=True)

        self.nav_items[key] = {"row": row, "icon": ico, "text": txt,
                               "name": icon_name, "active": active}

        def enter(event=None):
            if not self.nav_items[key]["active"]:
                row.configure(fg_color=PALETTE["hover"])
                ico.configure(image=icon(icon_name, PALETTE["brand"], 20))

        def leave(event=None):
            if not self.nav_items[key]["active"]:
                row.configure(fg_color="transparent")
                ico.configure(image=icon(icon_name, PALETTE["muted"], 20))

        def click(event=None):
            if key != "home":
                self.open(key)

        for w in (row, ico, txt):
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)
            w.bind("<Button-1>", click)
            w.configure(cursor="hand2")

    # =================================================================
    # HEADER
    # =================================================================

    def build_header(self, parent):

        header = ctk.CTkFrame(
            parent, fg_color=PALETTE["surface"], height=76, corner_radius=0
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkFrame(parent, fg_color=PALETTE["border"], height=1, corner_radius=0).pack(fill="x")

        # ---- Recherche ----
        search = ctk.CTkFrame(
            header, fg_color=PALETTE["surface"], corner_radius=10,
            border_width=1, border_color=PALETTE["border"], width=380, height=44
        )
        search.pack(side="left", padx=(30, 0), pady=16)
        search.pack_propagate(False)

        ctk.CTkLabel(
            search, text="", image=icon("search", PALETTE["muted"], 18),
            fg_color="transparent"
        ).pack(side="left", padx=(14, 6))

        ctk.CTkEntry(
            search, textvariable=self.search_var, font=self.f_search,
            placeholder_text="Rechercher un module...",
            fg_color="transparent", border_width=0,
            text_color=PALETTE["text"], placeholder_text_color=PALETTE["muted"]
        ).pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.search_var.trace_add("write", lambda *_: self.render_cards())

        # ---- Zone droite ----
        avatar = ctk.CTkFrame(
            header, fg_color=PALETTE["brand_soft"], width=42, height=42, corner_radius=21
        )
        avatar.pack(side="right", padx=(12, 30))
        avatar.pack_propagate(False)
        ctk.CTkLabel(
            avatar, text="RA", font=self.f_avatar,
            text_color=PALETTE["brand"], fg_color="transparent"
        ).pack(expand=True)

        bell = ctk.CTkFrame(
            header, fg_color=PALETTE["surface"], width=42, height=42, corner_radius=21,
            border_width=1, border_color=PALETTE["border"]
        )
        bell.pack(side="right", padx=(12, 0))
        bell.pack_propagate(False)
        ctk.CTkLabel(
            bell, text="", image=icon("bell", PALETTE["muted"], 18),
            fg_color="transparent"
        ).pack(expand=True)

        status = ctk.CTkFrame(
            header, fg_color=PALETTE["success_bg"], corner_radius=18, height=34
        )
        status.pack(side="right", pady=21)

        ctk.CTkFrame(
            status, fg_color=PALETTE["success"], width=8, height=8, corner_radius=4
        ).pack(side="left", padx=(14, 8), pady=13)

        ctk.CTkLabel(
            status, text="Système opérationnel", font=self.f_status,
            text_color=PALETTE["success_txt"], fg_color="transparent"
        ).pack(side="left", padx=(0, 14))

    # =================================================================
    # FOOTER
    # =================================================================

    def build_footer(self, parent):

        footer = ctk.CTkFrame(
            parent, fg_color=PALETTE["surface"], height=44, corner_radius=0
        )
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        ctk.CTkFrame(parent, fg_color=PALETTE["border"], height=1, corner_radius=0).pack(
            fill="x", side="bottom"
        )

        ctk.CTkLabel(
            footer, text="Revenue Assurance  •  RA Control Center", font=self.f_footer,
            text_color=PALETTE["muted"], fg_color="transparent"
        ).pack(side="left", padx=30)

        ctk.CTkLabel(
            footer, text="v1.0", font=self.f_footer,
            text_color=PALETTE["muted"], fg_color="transparent"
        ).pack(side="right", padx=30)

    # =================================================================
    # BODY
    # =================================================================

    def build_body(self, parent):

        body = ctk.CTkFrame(parent, fg_color=PALETTE["bg"], corner_radius=0)
        body.pack(fill="both", expand=True, padx=30, pady=(26, 20))

        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x", pady=(0, 24))

        left = ctk.CTkFrame(top, fg_color="transparent")
        left.pack(side="left")

        ctk.CTkLabel(
            left, text="Modules Revenue Assurance", font=self.f_page,
            text_color=PALETTE["text"], fg_color="transparent"
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Sélectionnez un domaine pour ouvrir son environnement de contrôle.",
            font=self.f_hint, text_color=PALETTE["muted"], fg_color="transparent"
        ).pack(anchor="w", pady=(4, 0))

        crumb = ctk.CTkLabel(
            top, text="Accueil  /  Modules", font=self.f_hint,
            text_color=PALETTE["muted"], fg_color="transparent"
        )
        crumb.pack(side="right", anchor="n", pady=8)

        self.grid_area = ctk.CTkFrame(body, fg_color="transparent")
        self.grid_area.pack(fill="both", expand=True)

        for c in range(3):
            self.grid_area.grid_columnconfigure(c, weight=1, uniform="col")
        for r in range(2):
            self.grid_area.grid_rowconfigure(r, weight=1, uniform="row")

        self.render_cards()

    def render_cards(self):

        for w in self.grid_area.winfo_children():
            w.destroy()

        query = self.search_var.get().strip().lower()

        modules = [
            m for m in self.MODULES
            if not query or query in m[0].lower() or query in m[1].lower()
        ]

        if not modules:
            ctk.CTkLabel(
                self.grid_area, text="Aucun module ne correspond à votre recherche.",
                font=self.f_hint, text_color=PALETTE["muted"], fg_color="transparent"
            ).grid(row=0, column=0, columnspan=3, pady=40)
            return

        for i, module in enumerate(modules):
            card = self.build_card(self.grid_area, module)
            card.grid(row=i // 3, column=i % 3, sticky="nsew", padx=8, pady=8)

    # =================================================================
    # CARTE MODULE
    # =================================================================

    def build_card(self, parent, module):

        name, desc, icon_name, key = module
        available = key in self.AVAILABLE

        card = ctk.CTkFrame(
            parent, fg_color=PALETTE["surface"], corner_radius=16,
            border_width=1, border_color=PALETTE["border"]
        )

        # ---- Ligne haute : icône + badge ----
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=24, pady=(24, 0))

        icon_box = ctk.CTkFrame(
            top, fg_color=PALETTE["brand_soft"], width=56, height=56, corner_radius=14
        )
        icon_box.pack(side="left")
        icon_box.pack_propagate(False)

        ctk.CTkLabel(
            icon_box, text="", image=icon(icon_name, PALETTE["brand"], 26),
            fg_color="transparent"
        ).pack(expand=True)

        ctk.CTkLabel(
            top,
            text="  Disponible  " if available else "  Bientôt  ",
            font=self.f_badge, height=22, corner_radius=11,
            text_color=PALETTE["success_txt"] if available else PALETTE["muted"],
            fg_color=PALETTE["success_bg"] if available else PALETTE["neutral_bg"]
        ).pack(side="right", anchor="n")

        # ---- Texte ----
        ctk.CTkLabel(
            card, text=name, font=self.f_card_name,
            text_color=PALETTE["text"], fg_color="transparent"
        ).pack(anchor="w", padx=24, pady=(18, 0))

        ctk.CTkLabel(
            card, text=desc, font=self.f_card_desc,
            text_color=PALETTE["muted"], fg_color="transparent",
            wraplength=290, justify="left"
        ).pack(anchor="w", padx=24, pady=(6, 20))

        # ---- Séparateur + CTA ----
        ctk.CTkFrame(card, height=1, fg_color=PALETTE["border"]).pack(fill="x", padx=24)

        cta = ctk.CTkFrame(card, fg_color="transparent")
        cta.pack(fill="x", padx=24, pady=16, side="bottom")

        cta_color = PALETTE["brand"] if available else PALETTE["muted"]

        ctk.CTkLabel(
            cta, text="Ouvrir le module" if available else "Bientôt disponible",
            font=self.f_card_cta, text_color=cta_color, fg_color="transparent"
        ).pack(side="left")

        ctk.CTkLabel(
            cta, text="", image=icon("arrow", cta_color, 18), fg_color="transparent"
        ).pack(side="right")

        # -----------------------------------------------------------
        # Interactions (clic + hover)
        # -----------------------------------------------------------

        def click(event=None):
            self.open(key)

        def enter(event=None):
            card.configure(border_color=PALETTE["brand"])

        def leave(event=None):
            # ne pas quitter l'état hover si la souris passe sur un enfant
            try:
                x, y = card.winfo_pointerxy()
                under = card.winfo_containing(x, y)
                if under is not None and str(under).startswith(str(card)):
                    return
            except Exception:
                pass
            card.configure(border_color=PALETTE["border"])

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
        w.withdraw()
        w.title("RA • FIXE")
        w.geometry("1500x950")
        w.minsize(1250, 800)
        w.configure(fg_color=PALETTE["bg"])

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