import os
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageOps, ImageTk

ctk.set_appearance_mode("light")
ctk.set_widget_scaling(1.0)


# =====================================================================
# PALETTE
# =====================================================================

PALETTE = {
    "bg":          "#F7F8FA",
    "surface":     "#FFFFFF",
    "border":      "#E3E6EA",
    "text":        "#16181D",
    "text_soft":   "#4A4F58",
    "muted":       "#7B818C",
    "accent":      "#2F5FE0",
    "accent_soft": "#EEF2FD",
    "hero_dark":   "#0E1A2B",
}

FONT = "Segoe UI"
SERIF = "Georgia"


# =====================================================================
# EMPLACEMENT DES IMAGES
# =====================================================================
# Toutes les images sont des fichiers locaux, à déposer vous-même dans
# ce dossier. Rien n'est téléchargé ni généré : si un fichier manque,
# un simple bloc neutre l'indique à la place -- jamais d'illustration
# dessinée en remplacement.
#
# Résolutions minimales conseillées pour éviter tout flou à l'écran :
#   - hero.jpg          : au moins 1600 x 500 px (bannière très large)
#   - modules/<clé>.jpg : au moins 640 x 360 px  (ratio ~16:9)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
MODULES_DIR = os.path.join(ASSETS_DIR, "modules")

HERO_IMAGE_PATH = os.path.join(ASSETS_DIR, "hero.jpg")

MODULE_IMAGE_FILES = {
    "fixe":         "fixe.jpg",
    "ftth":         "ftth.jpg",
    "interconnect": "interconnect.jpg",
    "simbox":       "simbox.jpg",
    "a2p_p2a":      "a2p_p2a.jpg",
    "franchise":    "franchise.jpg",
}


# =====================================================================
# CHARGEMENT D'IMAGE HAUTE QUALITE ("cover", comme le CSS background-size)
# =====================================================================
#
# La photo source est recadrée pour remplir exactement la zone cible
# sans être déformée, avec un seul redimensionnement LANCZOS (le filtre
# le plus fin de Pillow). Si la photo source est plus petite que la zone
# cible, elle est agrandie -- privilégiez toujours une photo plus grande
# que nécessaire plutôt que plus petite.

_IMAGE_CACHE = {}


def _round_top_mask(w, h, radius):
    """
    Masque niveau de gris : coins hauts arrondis, coins bas carrés.
    Le rectangle arrondi dépasse la hauteur visible de `radius` en bas,
    ce qui pousse l'arrondi du bas hors du masque -- il ne reste donc
    que les deux coins du haut arrondis.
    """
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, w - 1, h - 1 + radius), radius=radius, fill=255)
    return mask


def _load_cover(path, target_w, target_h, round_top_radius=0):

    key = (path, target_w, target_h, round_top_radius)
    if key in _IMAGE_CACHE:
        return _IMAGE_CACHE[key]

    if not os.path.isfile(path):
        _IMAGE_CACHE[key] = None
        return None

    try:
        with Image.open(path) as raw:
            img = ImageOps.exif_transpose(raw)  # respecte l'orientation d'origine
            img = img.convert("RGB")

            src_w, src_h = img.size
            scale = max(target_w / src_w, target_h / src_h)
            new_w = max(1, round(src_w * scale))
            new_h = max(1, round(src_h * scale))

            resized = img.resize((new_w, new_h), Image.LANCZOS)

            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            cropped = resized.crop((left, top, left + target_w, top + target_h))

        if round_top_radius > 0:
            # transparence réelle sur les coins hauts -- pas de couleur
            # plaquée, pas de cadre carré posé par-dessus
            rgba = cropped.convert("RGBA")
            rgba.putalpha(_round_top_mask(target_w, target_h, round_top_radius))
            final = rgba
        else:
            final = cropped

        result = ctk.CTkImage(light_image=final, size=(target_w, target_h))

    except Exception:
        result = None

    _IMAGE_CACHE[key] = result
    return result


def module_image(key, width, height, round_top_radius=0):
    filename = MODULE_IMAGE_FILES.get(key)
    if not filename:
        return None
    return _load_cover(os.path.join(MODULES_DIR, filename), width, height, round_top_radius)


# =====================================================================
# HERO : photo pleine largeur + dégradé sombre intégré à l'image
# =====================================================================

_HERO_SOURCE = {"img": None, "loaded": False}


def _hero_source():
    """Charge la photo d'origine une seule fois (évite de relire le disque
    à chaque redimensionnement de la fenêtre)."""
    if not _HERO_SOURCE["loaded"]:
        _HERO_SOURCE["loaded"] = True
        if os.path.isfile(HERO_IMAGE_PATH):
            try:
                with Image.open(HERO_IMAGE_PATH) as raw:
                    _HERO_SOURCE["img"] = ImageOps.exif_transpose(raw).convert("RGB")
            except Exception:
                _HERO_SOURCE["img"] = None
    return _HERO_SOURCE["img"]


def _hero_pil(w, h, focus_y=0.40):
    """
    Photo 'cover' pleine largeur + dégradé sombre à gauche (intégré à
    l'image) pour garder le texte lisible. focus_y : 0 = haut de la photo,
    1 = bas (0.40 garde bien les sommets des pylônes).
    """
    src = _hero_source()
    if src is None:
        return None

    try:
        sw, sh = src.size
        scale = max(w / sw, h / sh)
        nw, nh = max(1, round(sw * scale)), max(1, round(sh * scale))
        img = src.resize((nw, nh), Image.LANCZOS)

        left = (nw - w) // 2
        top = round((nh - h) * focus_y)
        img = img.crop((left, top, left + w, top + h))

        # dégradé horizontal : opaque à gauche -> transparent vers 70 %
        grad_w = max(1, int(w * 0.70))
        grad = Image.linear_gradient("L").rotate(90, expand=True)   # 0 -> 255 gauche->droite
        grad = ImageOps.invert(grad).resize((grad_w, h), Image.BILINEAR)
        grad = grad.point(lambda v: int(v * 0.90))                  # opacité max 90 %

        mask = Image.new("L", (w, h), 0)
        mask.paste(grad, (0, 0))

        dark = Image.new("RGB", (w, h), PALETTE["hero_dark"])
        return Image.composite(dark, img, mask)

    except Exception:
        return None


# =====================================================================
# ICONES D'INTERFACE (dessinées avec Pillow -- uniquement pour les
# petits pictogrammes de l'UI : loupe, flèche, logo. Jamais utilisées
# comme substitut de photo.)
# =====================================================================

_ICON_CACHE = {}


def _draw_icon(name, color, size):
    S = 16
    N = 24 * S
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w = int(1.8 * S)

    def P(*pts):
        return [(x * S, y * S) for x, y in pts]

    def line(*pts):
        d.line(P(*pts), fill=color, width=w, joint="curve")
        r = w / 2
        for x, y in P(*pts):
            d.ellipse((x - r, y - r, x + r, y + r), fill=color)

    if name == "arrow":
        line((5, 12), (19, 12))
        line((13, 6), (19, 12), (13, 18))

    elif name == "search":
        d.ellipse(P((4, 4), (17, 17)), outline=color, width=w)
        line((15.5, 15.5), (20, 20))

    elif name == "logo":
        d.rounded_rectangle((0, 0, N - 1, N - 1), radius=5 * S, fill=color)
        white = (255, 255, 255, 255)
        pts = P((7, 12.5), (10.6, 16), (17, 8.5))
        d.line(pts, fill=white, width=int(2.2 * S), joint="curve")
        for x, y in (pts[0], pts[-1]):
            r = 1.1 * S
            d.ellipse((x - r, y - r, x + r, y + r), fill=white)

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
    # (nom, description, clé)
    MODULES = [
        ("FIXE",         "Dashboard Postpaid / Fixe",   "fixe"),
        ("FTTH",         "Contrôles Fibre",             "ftth"),
        ("INTERCONNECT", "Contrôles Interconnect",      "interconnect"),
        ("SIMBOX",       "Contrôles SIMBOX",            "simbox"),
        ("A2P / P2A",    "Messaging Revenue Assurance", "a2p_p2a"),
        ("FRANCHISE",    "Contrôles Franchise",         "franchise"),
    ]

    AVAILABLE = {"fixe"}

    CARD_W = 260
    CARD_H = 300
    IMG_H = 140

    HERO_H = 220

    def __init__(self):
        super().__init__()

        self.title("RA Control Center")
        self.geometry("1280x800")
        self.minsize(980, 640)
        self.configure(fg_color=PALETTE["bg"])

        self._fonts()
        self.build()

    # =================================================================
    # POLICES
    # =================================================================

    def _fonts(self):
        self.f_eyebrow = ctk.CTkFont(family=FONT, size=11, weight="bold")
        self.f_section = ctk.CTkFont(family=SERIF, size=20, weight="bold")
        self.f_hint = ctk.CTkFont(family=FONT, size=11)
        self.f_card_name = ctk.CTkFont(family=FONT, size=14, weight="bold")
        self.f_card_desc = ctk.CTkFont(family=FONT, size=10)
        self.f_missing = ctk.CTkFont(family=FONT, size=9)
        self.f_footer = ctk.CTkFont(family=FONT, size=9)

    # =================================================================
    # BUILD
    # =================================================================

    def build(self):

        self.build_hero()

        # le footer est empaqueté AVANT la section extensible, sinon
        # il peut être écrasé quand la fenêtre est petite
        self.build_footer()

        section = ctk.CTkFrame(self, fg_color=PALETTE["bg"], corner_radius=0)
        section.pack(fill="both", expand=True)

        head = ctk.CTkFrame(section, fg_color="transparent")
        head.pack(fill="x", padx=40, pady=(28, 4))

        ctk.CTkLabel(
            head, text="Nos modules", font=self.f_eyebrow,
            text_color=PALETTE["accent"], fg_color="transparent"
        ).pack(anchor="w")

        ctk.CTkLabel(
            head, text="Un module par périmètre de contrôle", font=self.f_section,
            text_color=PALETTE["text"], fg_color="transparent"
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(
            head,
            text="Faites défiler pour découvrir chaque environnement de contrôle "
                 "Revenue Assurance disponible.",
            font=self.f_hint, text_color=PALETTE["muted"], fg_color="transparent"
        ).pack(anchor="w", pady=(4, 0))

        # ---- Rangée à défilement HORIZONTAL, uniquement sur les cartes ----
        strip = ctk.CTkFrame(section, fg_color="transparent")
        strip.pack(fill="both", expand=True, padx=40, pady=(18, 30))

        self.rail = ctk.CTkScrollableFrame(
            strip, fg_color="transparent", corner_radius=0,
            orientation="horizontal", height=self.CARD_H + 26,
            scrollbar_button_color=PALETTE["border"],
            scrollbar_button_hover_color=PALETTE["muted"]
        )
        self.rail.pack(fill="both", expand=True)

        self.render_modules()

    # =================================================================
    # HERO (Canvas pleine largeur : la photo suit la taille de la fenêtre)
    # =================================================================

    def build_hero(self):

        self._hero_job = None
        self._hero_photo = None
        self._hero_w = 0

        self.hero = tk.Canvas(
            self, height=self.HERO_H, bg=PALETTE["hero_dark"],
            highlightthickness=0, bd=0
        )
        self.hero.pack(fill="x")
        self.hero.bind("<Configure>", self._on_hero_resize)

    def _on_hero_resize(self, event):
        if event.width <= 1 or event.width == self._hero_w:
            return
        self._hero_w = event.width
        if self._hero_job:
            self.after_cancel(self._hero_job)
        self._hero_job = self.after(40, lambda: self._draw_hero(event.width))

    def _draw_hero(self, w):

        self._hero_job = None

        h = self.HERO_H
        c = self.hero
        c.delete("all")

        photo = _hero_pil(w, h)

        if photo is not None:
            self._hero_photo = ImageTk.PhotoImage(photo)   # garder la référence
            c.create_image(0, 0, image=self._hero_photo, anchor="nw")
        else:
            c.create_text(
                w // 2, h // 2, anchor="center", fill="#7B818C",
                font=(FONT, 9), width=520, justify="center",
                text="assets/hero.jpg introuvable -- déposez une photo "
                     "télécom (au moins 1600×500 px) à cet emplacement."
            )

        cy = h // 2
        x = 48

        c.create_text(x, cy - 62, anchor="w", fill="#9FB3DE",
                      font=(FONT, 11, "bold"),
                      text="REVENUE ASSURANCE  •  CONTROL CENTER")

        c.create_text(x, cy - 22, anchor="w", fill="#FFFFFF",
                      font=(SERIF, 30, "bold"),
                      text="Un point d'entrée unique pour piloter vos contrôles")

        c.create_text(x, cy + 38, anchor="w", fill="#C7D3EA",
                      font=(FONT, 12), justify="left",
                      text="Fixe, Fibre, Interconnexion, SIMBOX, Messaging et Franchise --\n"
                           "chaque module ouvre son propre environnement de suivi.")

    def _missing_notice(self, parent, message):
        """Bloc neutre affiché quand une image locale n'a pas encore été déposée."""

        ctk.CTkLabel(
            parent, text=message, font=self.f_missing,
            text_color="#7B818C", fg_color="transparent",
            wraplength=520, justify="center"
        ).place(relx=0.5, rely=0.5, anchor="center")

    # =================================================================
    # CARTES DE MODULE (défilement horizontal)
    # =================================================================

    def render_modules(self):

        for w in self.rail.winfo_children():
            w.destroy()

        for module in self.MODULES:
            card = self.build_module_card(self.rail, module)
            card.pack(side="left", padx=(0, 16), pady=4)

    def build_module_card(self, parent, module):

        name, desc, key = module
        available = key in self.AVAILABLE

        card = ctk.CTkFrame(
            parent, fg_color=PALETTE["surface"], corner_radius=14,
            border_width=1, border_color=PALETTE["border"],
            width=self.CARD_W, height=self.CARD_H, cursor="hand2"
        )
        card.pack_propagate(False)

        # ---- Zone photo ----
        # L'image (recadrée + arrondie sur ses deux coins hauts, avec
        # une vraie transparence) est posée directement sur la carte,
        # sans cadre intermédiaire : le contour rond de la carte reste
        # visible tel qu'il est dessiné, aucun angle carré ne dépasse.
        img = module_image(key, self.CARD_W - 2, self.IMG_H, round_top_radius=13)

        if img is not None:
            img_widget = ctk.CTkLabel(card, text="", image=img, fg_color="transparent")
            img_widget.place(x=1, y=1)
        else:
            img_widget = ctk.CTkFrame(
                card, fg_color=PALETTE["accent_soft"], corner_radius=0,
                width=self.CARD_W - 2, height=self.IMG_H
            )
            img_widget.place(x=1, y=1)
            self._missing_notice(
                img_widget,
                f"assets/modules/{MODULE_IMAGE_FILES.get(key, '?')} manquant"
            )

        # ---- Texte ----
        text_zone = ctk.CTkFrame(
            card, fg_color="transparent",
            width=self.CARD_W - 36, height=self.CARD_H - self.IMG_H - 30
        )
        text_zone.place(x=18, y=self.IMG_H + 16)

        ctk.CTkLabel(
            text_zone, text=name, font=self.f_card_name,
            text_color=PALETTE["text"], fg_color="transparent", anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_zone, text=desc, font=self.f_card_desc,
            text_color=PALETTE["muted"], fg_color="transparent",
            anchor="w", justify="left", wraplength=self.CARD_W - 36
        ).pack(anchor="w", pady=(6, 0))

        if not available:
            ctk.CTkLabel(
                text_zone, text="Bientôt disponible", font=self.f_card_desc,
                text_color=PALETTE["accent"], fg_color="transparent", anchor="w"
            ).pack(anchor="w", pady=(10, 0))

        # -----------------------------------------------------------
        # Interactions
        # -----------------------------------------------------------

        def click(event=None):
            self.open(key)

        def enter(event=None):
            card.configure(border_color=PALETTE["accent"])

        def leave(event=None):
            try:
                x, y = card.winfo_pointerxy()
                under = card.winfo_containing(x, y)
                if under is not None and str(under).startswith(str(card)):
                    return
            except Exception:
                pass
            card.configure(border_color=PALETTE["border"])

        for widget in (card, img_widget, text_zone):
            widget.bind("<Button-1>", click)
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)
            try:
                widget.configure(cursor="hand2")
            except Exception:
                pass

        for child in text_zone.winfo_children():
            child.bind("<Button-1>", click)
            child.configure(cursor="hand2")

        return card

    # =================================================================
    # FOOTER
    # =================================================================

    def build_footer(self):

        ctk.CTkFrame(self, fg_color=PALETTE["border"], height=1, corner_radius=0).pack(
            fill="x", side="bottom"
        )

        footer = ctk.CTkFrame(self, fg_color=PALETTE["surface"], height=40, corner_radius=0)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        ctk.CTkLabel(
            footer, text="Revenue Assurance  •  RA Control Center", font=self.f_footer,
            text_color=PALETTE["muted"], fg_color="transparent"
        ).pack(side="left", padx=40)

        ctk.CTkLabel(
            footer, text="v1.0", font=self.f_footer,
            text_color=PALETTE["muted"], fg_color="transparent"
        ).pack(side="right", padx=40)

    # =================================================================
    # OUVERTURE D'UN MODULE
    # =================================================================

    def openOld(self, key):
        print(f"Ouverture du module {key.upper()}...")
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

        # Cacher le Control Center
        self.withdraw()

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

            # Réafficher le Control Center si erreur
            self.deiconify()
            self.lift()
            messagebox.showerror("Erreur Dashboard FIXE", str(e), parent=self)
            return

        w.after(10, w.deiconify)  # affiche seulement une fois le contenu construit

    # Quand le dashboard est fermé
    

    def open(self, key):
        print(f"Ouverture du module {key.upper()}...")

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

        # Cacher le Control Center
        self.withdraw()

        def on_module_close():
            try:
                w.destroy()
            finally:
                self.deiconify()
                self.lift()
                self.focus_force()

        w = ctk.CTkToplevel(self)
        w.withdraw()

        w.title("RA • FIXE")
        w.geometry("1500x950")
        w.minsize(1250, 800)
        w.configure(fg_color=PALETTE["bg"])

        try:
            w.tk.call("tk", "scaling", 1.20)
        except Exception:
            pass

        try:
            Dashboard(
                w,
                perimetre="FXL",
                mode_execution="COMMIT",
                on_close=on_module_close
            )
        except TypeError:
            Dashboard(w)
        except Exception as e:
            w.destroy()
            # Réafficher le Control Center si erreur
            self.deiconify()
            self.lift()
            messagebox.showerror(
                "Erreur Dashboard FIXE",
                str(e),
                parent=self
            )
            return

        w.protocol("WM_DELETE_WINDOW", on_module_close)
        w.after(10, w.deiconify)
        w.after(50, w.lift)