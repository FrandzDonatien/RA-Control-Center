"""
BillingFixControl - Interface de gestion (CustomTkinter)
=============================================================
Thème clair inspiré de TailAdmin (demo.tailadmin.com) :
sidebar de navigation, cartes blanches arrondies, badges de statut,
tableaux épurés, icônes vectorielles générées (pas d'émojis),
pages dédiées pour l'ajout/modification (pas de modales),
et un effet de chargement "skeleton" sur le dashboard.

Installation requise :
    pip install customtkinter pillow

Police : l'app utilise "Outfit" (police officielle de TailAdmin, via Google
Fonts : https://fonts.google.com/specimen/Outfit). Installez-la sur votre
système pour un rendu fidèle ; à défaut, l'app bascule automatiquement sur
Segoe UI.
"""

import math
import sqlite3
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import messagebox
from datetime import date

import customtkinter as ctk
from PIL import Image, ImageDraw


# ============================================================
# Palette (clair, inspirée de TailAdmin)
# ============================================================

COLOR_BODY_BG = "#F9FAFB"
COLOR_SIDEBAR_BG = "#FFFFFF"
COLOR_CARD_BG = "#FFFFFF"
COLOR_BORDER = "#E4E7EC"
COLOR_TEXT_PRIMARY = "#1D2939"
COLOR_TEXT_SECONDARY = "#667085"
COLOR_ACCENT = "#465FFF"
COLOR_ACCENT_HOVER = "#3648D6"
COLOR_ACCENT_LIGHT = "#EEF2FF"
COLOR_ROW_ALT = "#F9FAFB"
COLOR_HEADER_BG = "#F9FAFB"
COLOR_SKELETON = "#EDEFF2"
COLOR_SKELETON_ALT = "#E3E6EA"

COLOR_SUCCESS = "#12B76A"
COLOR_SUCCESS_BG = "#ECFDF3"
COLOR_WARNING = "#F79009"
COLOR_WARNING_BG = "#FFFAEB"
COLOR_ERROR = "#F04438"
COLOR_ERROR_BG = "#FEF3F2"
COLOR_NEUTRAL = "#667085"
COLOR_NEUTRAL_BG = "#F2F4F7"

SEVERITY_STYLES = {
    "CRITIQUE": {"bg": COLOR_ERROR_BG, "fg": COLOR_ERROR},
    "ATTENTION": {"bg": COLOR_WARNING_BG, "fg": COLOR_WARNING},
    "OK": {"bg": COLOR_SUCCESS_BG, "fg": COLOR_SUCCESS},
    None: {"bg": COLOR_NEUTRAL_BG, "fg": COLOR_NEUTRAL},
}

FONT_FAMILY = "Outfit"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def _resolve_font(root):
    """Utilise Outfit (police de TailAdmin) si elle est installée,
    sinon bascule sur Segoe UI / Arial."""
    global FONT_FAMILY
    try:
        available = set(tkfont.families(root))
    except Exception:
        return
    if "Outfit" in available:
        FONT_FAMILY = "Outfit"
    elif "Segoe UI" in available:
        FONT_FAMILY = "Segoe UI"
    else:
        FONT_FAMILY = "Arial"


# ============================================================
# Icônes vectorielles (dessinées, pas d'émojis)
# ============================================================

_ICON_CACHE = {}


def _canvas(size, scale=4):
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img), s


def _finish(img, size):
    return img.resize((size, size), Image.LANCZOS)


def _draw_home(size, color):
    img, d, s = _canvas(size)
    w = max(2, s // 13)
    d.line([(s * 0.50, s * 0.10), (s * 0.12, s * 0.46)], fill=color, width=w)
    d.line([(s * 0.50, s * 0.10), (s * 0.88, s * 0.46)], fill=color, width=w)
    d.line([(s * 0.20, s * 0.44), (s * 0.20, s * 0.88)], fill=color, width=w)
    d.line([(s * 0.80, s * 0.44), (s * 0.80, s * 0.88)], fill=color, width=w)
    d.line([(s * 0.20, s * 0.88), (s * 0.80, s * 0.88)], fill=color, width=w)
    d.rectangle([s * 0.42, s * 0.60, s * 0.58, s * 0.88], outline=color, width=w)
    return _finish(img, size)


def _draw_list(size, color):
    img, d, s = _canvas(size)
    w = max(2, s // 11)
    for y in (0.24, 0.5, 0.76):
        d.ellipse([s * 0.09, s * y - s * 0.035, s * 0.09 + s * 0.07, s * y + s * 0.035], fill=color)
        d.line([(s * 0.28, s * y), (s * 0.90, s * y)], fill=color, width=w)
    return _finish(img, size)


def _draw_tag(size, color):
    img, d, s = _canvas(size)
    w = max(2, s // 11)
    pts = [(s * 0.14, s * 0.16), (s * 0.55, s * 0.16), (s * 0.90, s * 0.50),
           (s * 0.55, s * 0.86), (s * 0.14, s * 0.86)]
    d.polygon(pts, outline=color, width=w)
    d.ellipse([s * 0.27, s * 0.37, s * 0.40, s * 0.50], outline=color, width=w)
    return _finish(img, size)


def _draw_chart(size, color):
    img, d, s = _canvas(size)
    w = max(2, s // 9)
    for x, h in ((0.22, 0.42), (0.50, 0.68), (0.78, 0.28)):
        d.line([(s * x, s * 0.86), (s * x, s * (0.86 - h))], fill=color, width=w)
    return _finish(img, size)


def _draw_search(size, color):
    img, d, s = _canvas(size)
    w = max(2, s // 11)
    d.ellipse([s * 0.14, s * 0.14, s * 0.62, s * 0.62], outline=color, width=w)
    d.line([(s * 0.58, s * 0.58), (s * 0.88, s * 0.88)], fill=color, width=w)
    return _finish(img, size)


def _draw_plus(size, color):
    img, d, s = _canvas(size)
    w = max(2, s // 9)
    d.line([(s * 0.5, s * 0.15), (s * 0.5, s * 0.85)], fill=color, width=w)
    d.line([(s * 0.15, s * 0.5), (s * 0.85, s * 0.5)], fill=color, width=w)
    return _finish(img, size)


def _draw_arrow_left(size, color):
    img, d, s = _canvas(size)
    w = max(2, s // 9)
    d.line([(s * 0.86, s * 0.5), (s * 0.18, s * 0.5)], fill=color, width=w)
    d.line([(s * 0.40, s * 0.24), (s * 0.18, s * 0.5)], fill=color, width=w)
    d.line([(s * 0.40, s * 0.76), (s * 0.18, s * 0.5)], fill=color, width=w)
    return _finish(img, size)


def _draw_refresh(size, color):
    img, d, s = _canvas(size)
    w = max(2, s // 9)
    d.arc([s * 0.14, s * 0.14, s * 0.86, s * 0.86], start=-40, end=250, fill=color, width=w)
    cx, cy, r = s * 0.5, s * 0.5, s * 0.36
    ang = math.radians(250)
    ex, ey = cx + r * math.cos(ang), cy + r * math.sin(ang)
    d.polygon([(ex, ey - s * 0.09), (ex + s * 0.11, ey + s * 0.02), (ex - s * 0.02, ey + s * 0.11)], fill=color)
    return _finish(img, size)


def _draw_edit(size, color):
    img, d, s = _canvas(size)
    w = max(2, s // 11)
    d.line([(s * 0.18, s * 0.82), (s * 0.62, s * 0.38)], fill=color, width=w)
    d.line([(s * 0.62, s * 0.38), (s * 0.78, s * 0.22)], fill=color, width=w)
    d.line([(s * 0.78, s * 0.22), (s * 0.88, s * 0.32)], fill=color, width=w)
    d.line([(s * 0.88, s * 0.32), (s * 0.72, s * 0.48)], fill=color, width=w)
    d.line([(s * 0.72, s * 0.48), (s * 0.26, s * 0.90)], fill=color, width=w)
    d.line([(s * 0.18, s * 0.82), (s * 0.26, s * 0.90)], fill=color, width=w)
    return _finish(img, size)


def _draw_trash(size, color):
    img, d, s = _canvas(size)
    w = max(2, s // 11)
    d.line([(s * 0.18, s * 0.30), (s * 0.82, s * 0.30)], fill=color, width=w)
    d.line([(s * 0.38, s * 0.30), (s * 0.40, s * 0.17)], fill=color, width=w)
    d.line([(s * 0.62, s * 0.30), (s * 0.60, s * 0.17)], fill=color, width=w)
    d.line([(s * 0.40, s * 0.17), (s * 0.60, s * 0.17)], fill=color, width=w)
    d.rectangle([s * 0.26, s * 0.30, s * 0.74, s * 0.87], outline=color, width=w)
    d.line([(s * 0.42, s * 0.42), (s * 0.42, s * 0.76)], fill=color, width=max(1, w - 2))
    d.line([(s * 0.58, s * 0.42), (s * 0.58, s * 0.76)], fill=color, width=max(1, w - 2))
    return _finish(img, size)


_ICON_DRAWERS = {
    "home": _draw_home, "list": _draw_list, "tag": _draw_tag, "chart": _draw_chart,
    "search": _draw_search, "plus": _draw_plus, "arrow-left": _draw_arrow_left,
    "refresh": _draw_refresh, "edit": _draw_edit, "trash": _draw_trash,
}


def get_icon(name, size=18, color=COLOR_TEXT_SECONDARY):
    key = (name, size, color)
    if key not in _ICON_CACHE:
        pil_img = _ICON_DRAWERS[name](size, color)
        _ICON_CACHE[key] = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(size, size))
    return _ICON_CACHE[key]


def make_sparkline(values, width=64, height=30, color=COLOR_ACCENT):
    """Génère un petit graphique en mini-courbe (sparkline)."""
    scale = 3
    w, h = width * scale, height * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    vals = list(values) or [0]
    if len(vals) == 1:
        vals = vals * 2
    vmin, vmax = min(vals), max(vals)
    span = (vmax - vmin) or 1
    n = len(vals)
    pad = h * 0.18
    pts = []
    for i, v in enumerate(vals):
        x = (i / (n - 1)) * w if n > 1 else 0
        y = h - pad - ((v - vmin) / span) * (h - 2 * pad)
        pts.append((x, y))
    d.line(pts, fill=color, width=max(2, scale + 1), joint="curve")
    lx, ly = pts[-1]
    r = scale * 1.7
    d.ellipse([lx - r, ly - r, lx + r, ly + r], fill=color)
    return img.resize((width, height), Image.LANCZOS)


# ============================================================
# Configuration / Connexion à la base
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "billingfixcontrol.db"


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_database():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ra_controls_catalog (
                control_id INTEGER PRIMARY KEY,
                control_name TEXT NOT NULL,
                famille TEXT,
                frequence TEXT,
                description TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ra_controls_catalog_category (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL
            )
        """)

        cursor.executemany("""
            INSERT OR IGNORE INTO ra_controls_catalog_category (id, category)
            VALUES (?, ?)
        """, [(1, "FXL"), (2, "HYB")])

        controls = [
            (1, "Clients actifs vs run de facturation", "Population", "Journalier",
             "Verifie que tous les actifs postpaid sont factures"),
            (2, "Reconciliation entre cycles consecutifs", "Population", "Mensuel",
             "Detecte les abonnes disparus d'un cycle a l'autre"),
            (3, "Validation des calculs de facturation", "Exactitude", "Mensuel",
             "Recalcul independant des montants factures"),
            (4, "Analyse de variance mois/mois", "Exactitude", "Mensuel",
             "Suivi ARPU, revenu, nb abonnes"),
            (5, "Validation du prorata", "Exactitude", "Journalier",
             "Controle des factures au prorata"),
            (6, "Facturation a 0 / hors seuils", "Exactitude", "Journalier",
             "Detection des prix aberrants"),
            (7, "Montant minimum du plan", "Exactitude", "Journalier",
             "Verifie le respect du minimum facturable"),
            (8, "Frais uniques", "Charges specifiques", "Journalier",
             "Installation, penalites, reconnexion"),
            (9, "Usage vs facturation", "Charges specifiques", "Journalier",
             "Voix, data, SMS, roaming, VAS"),
            (10, "Promotions expirees", "Charges specifiques", "Journalier",
             "Remises appliquees au-dela de leur validite"),
            (11, "Revue echantillon de factures", "Revue qualitative", "Mensuel",
             "Revue manuelle documentee"),
            (12, "Analyse de marge / revenue assurance", "Revue qualitative", "Mensuel",
             "Cout de service vs revenu facture"),
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO ra_controls_catalog
            (control_id, control_name, famille, frequence, description)
            VALUES (?, ?, ?, ?, ?)
        """, controls)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ra_controls_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                control_id INTEGER NOT NULL,
                catalog_category_id INTEGER NOT NULL,
                date_controle DATE NOT NULL,
                categorie TEXT NOT NULL,
                nb_items INTEGER NOT NULL DEFAULT 0,
                montant_impacte REAL,
                severite TEXT NOT NULL CHECK (severite IN ('OK', 'ATTENTION', 'CRITIQUE')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (control_id, date_controle, categorie),
                FOREIGN KEY (control_id) REFERENCES ra_controls_catalog(control_id),
                FOREIGN KEY (catalog_category_id) REFERENCES ra_controls_catalog_category(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ra_controls_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                control_id INTEGER NOT NULL,
                catalog_category_id INTEGER NOT NULL,
                date_controle DATE NOT NULL,
                cle_metier TEXT NOT NULL,
                categorie TEXT NOT NULL,
                detail TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (control_id) REFERENCES ra_controls_catalog(control_id),
                FOREIGN KEY (catalog_category_id) REFERENCES ra_controls_catalog_category(id)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ra_controls_log_date
            ON ra_controls_log (date_controle)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ra_controls_details_date
            ON ra_controls_details (control_id, date_controle)
        """)

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ============================================================
# Couche d'accès aux données (DAO)
# ============================================================

def fetch_categories():
    conn = get_connection()
    rows = conn.execute("SELECT id, category FROM ra_controls_catalog_category ORDER BY id").fetchall()
    conn.close()
    return rows


def insert_category(name):
    conn = get_connection()
    conn.execute("INSERT INTO ra_controls_catalog_category (category) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def delete_category(cat_id):
    conn = get_connection()
    conn.execute("DELETE FROM ra_controls_catalog_category WHERE id = ?", (cat_id,))
    conn.commit()
    conn.close()


def fetch_controls():
    conn = get_connection()
    rows = conn.execute("""
        SELECT control_id, control_name, famille, frequence, description
        FROM ra_controls_catalog ORDER BY control_id
    """).fetchall()
    conn.close()
    return rows


def next_control_id():
    conn = get_connection()
    row = conn.execute("SELECT COALESCE(MAX(control_id), 0) + 1 AS nid FROM ra_controls_catalog").fetchone()
    conn.close()
    return row["nid"]


def insert_control(control_id, name, famille, frequence, description):
    conn = get_connection()
    conn.execute("""
        INSERT INTO ra_controls_catalog (control_id, control_name, famille, frequence, description)
        VALUES (?, ?, ?, ?, ?)
    """, (control_id, name, famille, frequence, description))
    conn.commit()
    conn.close()


def update_control(control_id, name, famille, frequence, description):
    conn = get_connection()
    conn.execute("""
        UPDATE ra_controls_catalog
        SET control_name = ?, famille = ?, frequence = ?, description = ?
        WHERE control_id = ?
    """, (name, famille, frequence, description, control_id))
    conn.commit()
    conn.close()


def delete_control(control_id):
    conn = get_connection()
    conn.execute("DELETE FROM ra_controls_catalog WHERE control_id = ?", (control_id,))
    conn.commit()
    conn.close()


def fetch_logs(date_from=None, date_to=None, severite=None):
    conn = get_connection()
    query = """
        SELECT l.id, l.control_id, c.control_name, l.catalog_category_id, cat.category,
               l.date_controle, l.categorie, l.nb_items, l.montant_impacte, l.severite
        FROM ra_controls_log l
        JOIN ra_controls_catalog c ON c.control_id = l.control_id
        JOIN ra_controls_catalog_category cat ON cat.id = l.catalog_category_id
        WHERE 1=1
    """
    params = []
    if date_from:
        query += " AND l.date_controle >= ?"
        params.append(date_from)
    if date_to:
        query += " AND l.date_controle <= ?"
        params.append(date_to)
    if severite and severite != "Toutes":
        query += " AND l.severite = ?"
        params.append(severite)
    query += " ORDER BY l.date_controle DESC, l.id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def insert_log(control_id, catalog_category_id, date_controle, categorie, nb_items, montant_impacte, severite):
    conn = get_connection()
    conn.execute("""
        INSERT INTO ra_controls_log
        (control_id, catalog_category_id, date_controle, categorie, nb_items, montant_impacte, severite)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (control_id, catalog_category_id, date_controle, categorie, nb_items, montant_impacte, severite))
    conn.commit()
    conn.close()


def delete_log(log_id):
    conn = get_connection()
    conn.execute("DELETE FROM ra_controls_log WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()


def fetch_details(control_id=None, date_controle=None):
    conn = get_connection()
    query = """
        SELECT d.id, d.control_id, c.control_name, cat.category, d.date_controle,
               d.cle_metier, d.categorie, d.detail
        FROM ra_controls_details d
        JOIN ra_controls_catalog c ON c.control_id = d.control_id
        JOIN ra_controls_catalog_category cat ON cat.id = d.catalog_category_id
        WHERE 1=1
    """
    params = []
    if control_id:
        query += " AND d.control_id = ?"
        params.append(control_id)
    if date_controle:
        query += " AND d.date_controle = ?"
        params.append(date_controle)
    query += " ORDER BY d.date_controle DESC, d.id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def insert_detail(control_id, catalog_category_id, date_controle, cle_metier, categorie, detail):
    conn = get_connection()
    conn.execute("""
        INSERT INTO ra_controls_details
        (control_id, catalog_category_id, date_controle, cle_metier, categorie, detail)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (control_id, catalog_category_id, date_controle, cle_metier, categorie, detail))
    conn.commit()
    conn.close()


def delete_detail(detail_id):
    conn = get_connection()
    conn.execute("DELETE FROM ra_controls_details WHERE id = ?", (detail_id,))
    conn.commit()
    conn.close()


def fetch_latest_status():
    """Dernier statut (nb_items, sévérité, date) par contrôle -> dict {control_id: Row}."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT l.control_id, l.nb_items, l.severite, l.date_controle
        FROM ra_controls_log l
        INNER JOIN (
            SELECT control_id, MAX(date_controle) AS max_date
            FROM ra_controls_log
            GROUP BY control_id
        ) latest
        ON l.control_id = latest.control_id AND l.date_controle = latest.max_date
        ORDER BY l.id DESC
    """).fetchall()
    conn.close()
    result = {}
    for r in rows:
        result.setdefault(r["control_id"], r)
    return result


def fetch_last_execution():
    conn = get_connection()
    row = conn.execute("SELECT MAX(created_at) AS last_exec FROM ra_controls_log").fetchone()
    conn.close()
    return row["last_exec"]


def fetch_trend(severite=None, limit=7):
    """Nombre de résumés par jour (les `limit` derniers jours avec activité),
    utilisé pour dessiner les mini sparklines des cartes KPI."""
    conn = get_connection()
    if severite:
        rows = conn.execute("""
            SELECT date_controle, COUNT(*) AS cnt FROM ra_controls_log
            WHERE severite = ? GROUP BY date_controle ORDER BY date_controle DESC LIMIT ?
        """, (severite, limit)).fetchall()
    else:
        rows = conn.execute("""
            SELECT date_controle, COUNT(*) AS cnt FROM ra_controls_log
            GROUP BY date_controle ORDER BY date_controle DESC LIMIT ?
        """, (limit,)).fetchall()
    conn.close()
    return [r["cnt"] for r in reversed(rows)]


# ============================================================
# Widgets utilitaires
# ============================================================

def confirm(msg):
    return messagebox.askyesno("Confirmation", msg)


def make_badge(parent, text, bg, fg):
    return ctk.CTkLabel(
        parent, text=text, font=(FONT_FAMILY, 11, "bold"),
        fg_color=bg, text_color=fg, corner_radius=12,
        padx=10, pady=3,
    )


class Card(ctk.CTkFrame):
    """Carte blanche avec bordure fine, arrondie, façon TailAdmin."""

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent, fg_color=COLOR_CARD_BG, corner_radius=12,
            border_width=1, border_color=COLOR_BORDER, **kwargs
        )


class PageHeader(ctk.CTkFrame):
    def __init__(self, parent, title, subtitle=None, action_text=None,
                 action_command=None, action_icon="plus"):
        super().__init__(parent, fg_color="transparent")
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", anchor="w")
        ctk.CTkLabel(left, text=title, font=(FONT_FAMILY, 20, "bold"),
                     text_color=COLOR_TEXT_PRIMARY).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(left, text=subtitle, font=(FONT_FAMILY, 12),
                         text_color=COLOR_TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))
        if action_text:
            ctk.CTkButton(
                self, text=action_text, image=get_icon(action_icon, 15, "white"),
                compound="left", command=action_command,
                fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER,
                font=(FONT_FAMILY, 12, "bold"), corner_radius=8, height=36,
            ).pack(side="right", anchor="e")


class BackButton(ctk.CTkButton):
    def __init__(self, parent, command):
        super().__init__(
            parent, text="Retour", image=get_icon("arrow-left", 15, COLOR_TEXT_SECONDARY),
            compound="left", command=command,
            fg_color="white", text_color=COLOR_TEXT_SECONDARY, hover_color=COLOR_NEUTRAL_BG,
            border_width=1, border_color=COLOR_BORDER, corner_radius=8, height=34, width=104,
            font=(FONT_FAMILY, 12),
        )


class FormDialog(ctk.CTkToplevel):
    """Boîte de dialogue générique (utilisée pour Résumés / Détails)."""

    def __init__(self, parent, title, fields, initial=None):
        super().__init__(parent)
        self.title(title)
        self.configure(fg_color=COLOR_BODY_BG)
        self.resizable(False, False)
        self.result = None
        self.vars = {}
        self.widgets = {}

        initial = initial or {}
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(padx=20, pady=20)

        ctk.CTkLabel(container, text=title, font=(FONT_FAMILY, 15, "bold"),
                     text_color=COLOR_TEXT_PRIMARY).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        for i, field in enumerate(fields, start=1):
            label, key = field[0], field[1]
            ftype = field[2]
            ctk.CTkLabel(container, text=label, font=(FONT_FAMILY, 12),
                         text_color=COLOR_TEXT_SECONDARY).grid(row=i, column=0, sticky="w", pady=6, padx=(0, 12))

            if ftype == "entry":
                var = tk.StringVar(value=initial.get(key, ""))
                w = ctk.CTkEntry(container, textvariable=var, width=260, corner_radius=8,
                                  border_color=COLOR_BORDER, fg_color="white")
                self.vars[key] = var
            elif ftype == "text":
                w = ctk.CTkTextbox(container, width=260, height=80, corner_radius=8,
                                    border_width=1, border_color=COLOR_BORDER, fg_color="white")
                w.insert("1.0", initial.get(key, ""))
                self.widgets[key] = w
            elif ftype == "combo":
                options = field[3]
                var = tk.StringVar(value=initial.get(key, options[0] if options else ""))
                w = ctk.CTkComboBox(container, variable=var, values=options, width=260,
                                     corner_radius=8, border_color=COLOR_BORDER,
                                     button_color=COLOR_ACCENT, fg_color="white", state="readonly")
                self.vars[key] = var

            w.grid(row=i, column=1, pady=6)

        btns = ctk.CTkFrame(container, fg_color="transparent")
        btns.grid(row=len(fields) + 1, column=0, columnspan=2, pady=(16, 0), sticky="e")
        ctk.CTkButton(btns, text="Annuler", command=self.destroy, fg_color=COLOR_NEUTRAL_BG,
                      text_color=COLOR_TEXT_PRIMARY, hover_color=COLOR_BORDER,
                      corner_radius=8).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btns, text="Enregistrer", command=self._on_save, fg_color=COLOR_ACCENT,
                      hover_color=COLOR_ACCENT_HOVER, corner_radius=8).pack(side="left")

        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _on_save(self):
        result = {}
        for key, var in self.vars.items():
            result[key] = var.get()
        for key, widget in self.widgets.items():
            result[key] = widget.get("1.0", "end").strip()
        self.result = result
        self.destroy()


class TableFrame(ctk.CTkFrame):
    """Table épurée façon TailAdmin : en-tête + lignes dans une zone défilante."""

    def __init__(self, parent, columns):
        """columns: liste de (label, width, anchor)"""
        super().__init__(parent, fg_color=COLOR_CARD_BG, corner_radius=12,
                          border_width=1, border_color=COLOR_BORDER)
        self.columns = columns

        header = ctk.CTkFrame(self, fg_color=COLOR_HEADER_BG, corner_radius=0, height=44)
        header.pack(fill="x")
        header.pack_propagate(False)
        for label, width, anchor in columns:
            ctk.CTkLabel(header, text=label, font=(FONT_FAMILY, 11, "bold"),
                         text_color=COLOR_TEXT_SECONDARY, width=width, anchor=anchor
                         ).pack(side="left", padx=10)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=COLOR_CARD_BG, corner_radius=0, height=380)
        self.scroll.pack(fill="both", expand=True)

    def clear(self):
        for w in self.scroll.winfo_children():
            w.destroy()

    def add_row(self, cells, actions=None, alt=False):
        """cells: liste de valeurs (str) ou callables(parent)->widget.
        actions: liste de (icon_name, couleur, callback)."""
        row_bg = COLOR_ROW_ALT if alt else COLOR_CARD_BG
        row = ctk.CTkFrame(self.scroll, fg_color=row_bg, corner_radius=0, height=48)
        row.pack(fill="x")
        row.pack_propagate(False)

        for (label, width, anchor), cell in zip(self.columns, cells):
            if callable(cell):
                w = cell(row)
                w.pack(side="left", padx=10)
            else:
                ctk.CTkLabel(row, text=str(cell), font=(FONT_FAMILY, 12),
                             text_color=COLOR_TEXT_PRIMARY, width=width, anchor=anchor,
                             justify="left").pack(side="left", padx=10)

        if actions:
            action_box = ctk.CTkFrame(row, fg_color="transparent")
            action_box.pack(side="right", padx=10)
            for icon_name, color, cb in actions:
                ctk.CTkButton(action_box, text="", image=get_icon(icon_name, 15, color),
                              width=28, height=28, corner_radius=6,
                              fg_color="transparent", hover_color=COLOR_NEUTRAL_BG,
                              command=cb).pack(side="left", padx=2)


# ============================================================
# Page Dashboard (avec skeleton loading)
# ============================================================

class DashboardPage(ctk.CTkFrame):
    COLS = 4

    def __init__(self, parent):
        super().__init__(parent, fg_color=COLOR_BODY_BG)
        self.active_family = "Toutes les familles"
        self._loading = False
        self._pulse_state = False
        self._skeleton_blocks = []
        self._spark_refs = []
        self._build()

    def _build(self):
        PageHeader(self, "Registre des contrôles",
                   "Revenue Assurance — Facturation postpaid",
                   action_text="Actualiser", action_command=self.refresh, action_icon="refresh"
                   ).pack(fill="x", padx=24, pady=(20, 16))

        self.meta_label = ctk.CTkLabel(self, text="", font=(FONT_FAMILY, 11),
                                        text_color=COLOR_TEXT_SECONDARY, anchor="w")
        self.meta_label.pack(fill="x", padx=24, pady=(0, 16))

        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=24, pady=(0, 16))
        for i in range(4):
            self.kpi_frame.grid_columnconfigure(i, weight=1)

        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.pack(fill="x", padx=24, pady=(0, 12))

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=COLOR_BODY_BG)
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    # ---------- Orchestration ----------

    def refresh(self):
        self._render_skeleton()
        self.after(500, self._render_data)

    # ---------- Skeleton (effet de chargement) ----------

    def _skel_block(self, parent, corner_radius=6, **kwargs):
        b = ctk.CTkFrame(
            parent,
            fg_color=COLOR_SKELETON,
            corner_radius=corner_radius,
            **kwargs
        )
        self._skeleton_blocks.append(b)
        return b

    def _render_skeleton(self):
        self._loading = True
        self._skeleton_blocks = []

        for w in self.kpi_frame.winfo_children():
            w.destroy()
        for i in range(4):
            card = Card(self.kpi_frame, height=88)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            card.grid_propagate(False)
            self._skel_block(card, width=80, height=10).place(x=16, y=18)
            self._skel_block(card, width=54, height=22).place(x=16, y=38)

        for w in self.filter_frame.winfo_children():
            w.destroy()
        for i in range(3):
            self._skel_block(self.filter_frame, width=110, height=30, corner_radius=16
                             ).pack(side="left", padx=(0, 8))

        for w in self.scroll.winfo_children():
            w.destroy()
        self._skel_block(self.scroll, width=200, height=16).pack(anchor="w", pady=(8, 12))
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="x")
        for i in range(self.COLS):
            grid.grid_columnconfigure(i, weight=1, uniform="card")
        for idx in range(8):
            row, col = divmod(idx, self.COLS)
            block = Card(grid, height=118)
            block.grid(row=row, column=col, sticky="nsew", padx=(0 if col == 0 else 8, 0), pady=(0, 12))
            block.grid_propagate(False)
            self._skel_block(block, width=60, height=10).place(x=14, y=16)
            self._skel_block(block, width=150, height=13).place(x=14, y=42)
            self._skel_block(block, width=40, height=20).place(x=14, y=80)

        self._pulse()

    def _pulse(self):
        if not self._loading:
            return
        color = COLOR_SKELETON_ALT if self._pulse_state else COLOR_SKELETON
        self._pulse_state = not self._pulse_state
        for b in self._skeleton_blocks:
            try:
                b.configure(fg_color=color)
            except Exception:
                pass
        self.after(350, self._pulse)

    # ---------- Données réelles ----------

    def _render_data(self):
        self._loading = False
        controls = fetch_controls()
        status = fetch_latest_status()
        last_exec = fetch_last_execution()

        self.meta_label.configure(
            text=(f"Dernière exécution : {last_exec}" if last_exec else "Aucune exécution enregistrée")
        )

        total = len(controls)
        n_crit = sum(1 for c in controls if status.get(c["control_id"], {}).get("severite") == "CRITIQUE")
        n_att = sum(1 for c in controls if status.get(c["control_id"], {}).get("severite") == "ATTENTION")
        n_ok = sum(1 for c in controls if status.get(c["control_id"], {}).get("severite") == "OK")

        for w in self.kpi_frame.winfo_children():
            w.destroy()
        self._spark_refs = []
        kpis = [
            ("Contrôles suivis", str(total), COLOR_ACCENT, None),
            ("En statut critique", str(n_crit), COLOR_ERROR, "CRITIQUE"),
            ("En attention", str(n_att), COLOR_WARNING, "ATTENTION"),
            ("Sans anomalie", str(n_ok), COLOR_SUCCESS, "OK"),
        ]
        for i, (label, num, spark_color, sev) in enumerate(kpis):
            card = Card(self.kpi_frame)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", padx=16, pady=14)
            ctk.CTkLabel(inner, text=label, font=(FONT_FAMILY, 12),
                         text_color=COLOR_TEXT_SECONDARY).pack(anchor="w")
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(anchor="w", pady=(6, 0), fill="x")
            ctk.CTkLabel(row, text=num, font=(FONT_FAMILY, 24, "bold"),
                         text_color=COLOR_TEXT_PRIMARY).pack(side="left")

            trend = fetch_trend(sev, limit=7)
            spark_pil = make_sparkline(trend, width=64, height=30, color=spark_color)
            spark_img = ctk.CTkImage(light_image=spark_pil, dark_image=spark_pil, size=(64, 30))
            self._spark_refs.append(spark_img)
            ctk.CTkLabel(row, image=spark_img, text="").pack(side="right")

        for w in self.filter_frame.winfo_children():
            w.destroy()
        families = []
        for c in controls:
            fam = c["famille"] or "Sans famille"
            if fam not in families:
                families.append(fam)
        options = ["Toutes les familles"] + families
        if self.active_family not in options:
            self.active_family = "Toutes les familles"

        for opt in options:
            active = opt == self.active_family
            ctk.CTkButton(
                self.filter_frame, text=opt,
                fg_color=COLOR_ACCENT if active else "white",
                text_color="white" if active else COLOR_TEXT_SECONDARY,
                hover_color=COLOR_ACCENT_HOVER if active else COLOR_NEUTRAL_BG,
                border_width=0 if active else 1, border_color=COLOR_BORDER,
                corner_radius=16, height=30, font=(FONT_FAMILY, 11, "bold" if active else "normal"),
                command=lambda o=opt: self._set_family(o),
            ).pack(side="left", padx=(0, 8))

        for w in self.scroll.winfo_children():
            w.destroy()

        grouped, order = {}, []
        for c in controls:
            fam = c["famille"] or "Sans famille"
            if self.active_family != "Toutes les familles" and fam != self.active_family:
                continue
            grouped.setdefault(fam, [])
            if fam not in order:
                order.append(fam)
            grouped[fam].append(c)

        for fam in order:
            ctk.CTkLabel(self.scroll, text=fam, font=(FONT_FAMILY, 14, "bold"),
                         text_color=COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(8, 10))

            grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
            grid.pack(fill="x", pady=(0, 6))
            for i in range(self.COLS):
                grid.grid_columnconfigure(i, weight=1, uniform="card")

            for idx, ctrl in enumerate(grouped[fam]):
                row, col = divmod(idx, self.COLS)
                self._build_card(grid, ctrl, status.get(ctrl["control_id"])).grid(
                    row=row, column=col, sticky="nsew", padx=(0 if col == 0 else 8, 0), pady=(0, 12))

    def _set_family(self, family):
        self.active_family = family
        self._render_data()

    def _build_card(self, parent, ctrl, status_row):
        severite = status_row["severite"] if status_row else None
        nb_items = status_row["nb_items"] if status_row else 0
        style = SEVERITY_STYLES.get(severite, SEVERITY_STYLES[None])

        card = Card(parent)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=12)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=f"CTRL-{ctrl['control_id']:02d}", font=(FONT_FAMILY, 10),
                     text_color=COLOR_TEXT_SECONDARY).pack(side="left")
        make_badge(top, severite or "N/A", style["bg"], style["fg"]).pack(side="right")

        ctk.CTkLabel(inner, text=ctrl["control_name"], font=(FONT_FAMILY, 13, "bold"),
                     text_color=COLOR_TEXT_PRIMARY, wraplength=210, justify="left"
                     ).pack(anchor="w", pady=(10, 12))

        bottom = ctk.CTkFrame(inner, fg_color="transparent")
        bottom.pack(fill="x")
        num_box = ctk.CTkFrame(bottom, fg_color="transparent")
        num_box.pack(side="left")
        ctk.CTkLabel(num_box, text=str(nb_items), font=(FONT_FAMILY, 20, "bold"),
                     text_color=COLOR_TEXT_PRIMARY).pack(anchor="w")
        suffix = "élément détecté" if nb_items == 1 else "éléments détectés"
        ctk.CTkLabel(num_box, text=suffix, font=(FONT_FAMILY, 10),
                     text_color=COLOR_TEXT_SECONDARY).pack(anchor="w")

        ctk.CTkLabel(bottom, text=ctrl["frequence"] or "", font=(FONT_FAMILY, 10),
                     text_color=COLOR_TEXT_SECONDARY).pack(side="right", anchor="s")

        return card


# ============================================================
# Catalogue : liste + page dédiée d'ajout/modification
# ============================================================

class CataloguePage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLOR_BODY_BG)
        self.app = app
        self._build()

    def _build(self):
        PageHeader(self, "Catalogue des contrôles",
                   "Liste des contrôles de facturation suivis",
                   action_text="Ajouter", action_command=self.add
                   ).pack(fill="x", padx=24, pady=(20, 16))

        columns = [
            ("Nom du contrôle", 260, "w"), ("Famille", 150, "w"),
            ("Fréquence", 100, "w"), ("Description", 260, "w"),
        ]
        self.table = TableFrame(self, columns)
        self.table.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def refresh(self):
        self.table.clear()
        for i, r in enumerate(fetch_controls()):
            self.table.add_row(
                [r["control_name"], r["famille"] or "-", r["frequence"] or "-", r["description"] or "-"],
                actions=[
                    ("edit", COLOR_ACCENT, lambda cid=r["control_id"]: self.edit(cid)),
                    ("trash", COLOR_ERROR, lambda cid=r["control_id"]: self.delete(cid)),
                ],
                alt=(i % 2 == 1),
            )

    def add(self):
        self.app.navigate("catalogue_form")

    def edit(self, control_id):
        self.app.navigate("catalogue_form", control_id=control_id)

    def delete(self, control_id):
        if confirm("Supprimer ce contrôle ? (les logs liés doivent être supprimés d'abord)"):
            try:
                delete_control(control_id)
                self.refresh()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erreur", "Ce contrôle est référencé par des logs existants.")


class CatalogueFormPage(ctk.CTkFrame):
    """Page dédiée (pas de modale) pour ajouter/modifier un contrôle."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLOR_BODY_BG)
        self.app = app
        self.editing_id = None
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 16))
        BackButton(header, command=lambda: self.app.navigate("catalogue")).pack(side="left")
        self.title_label = ctk.CTkLabel(header, text="Nouveau contrôle", font=(FONT_FAMILY, 18, "bold"),
                                         text_color=COLOR_TEXT_PRIMARY)
        self.title_label.pack(side="left", padx=16)

        card = Card(self)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(padx=24, pady=24, anchor="w")

        ctk.CTkLabel(form, text="Nom du contrôle", font=(FONT_FAMILY, 12),
                     text_color=COLOR_TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.name_entry = ctk.CTkEntry(form, width=380, corner_radius=8,
                                        border_color=COLOR_BORDER, fg_color="white")
        self.name_entry.grid(row=1, column=0, sticky="w", pady=(0, 14))

        ctk.CTkLabel(form, text="Famille", font=(FONT_FAMILY, 12),
                     text_color=COLOR_TEXT_SECONDARY).grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.famille_entry = ctk.CTkEntry(form, width=380, corner_radius=8,
                                           border_color=COLOR_BORDER, fg_color="white")
        self.famille_entry.grid(row=3, column=0, sticky="w", pady=(0, 14))

        ctk.CTkLabel(form, text="Fréquence", font=(FONT_FAMILY, 12),
                     text_color=COLOR_TEXT_SECONDARY).grid(row=4, column=0, sticky="w", pady=(0, 4))
        self.frequence_combo = ctk.CTkComboBox(form, values=["Journalier", "Mensuel", "Hebdomadaire"],
                                                width=380, corner_radius=8, border_color=COLOR_BORDER,
                                                button_color=COLOR_ACCENT, fg_color="white", state="readonly")
        self.frequence_combo.grid(row=5, column=0, sticky="w", pady=(0, 14))

        ctk.CTkLabel(form, text="Description", font=(FONT_FAMILY, 12),
                     text_color=COLOR_TEXT_SECONDARY).grid(row=6, column=0, sticky="w", pady=(0, 4))
        self.description_text = ctk.CTkTextbox(form, width=380, height=120, corner_radius=8,
                                                border_width=1, border_color=COLOR_BORDER, fg_color="white")
        self.description_text.grid(row=7, column=0, sticky="w", pady=(0, 20))

        ctk.CTkButton(form, text="Enregistrer", command=self._save, fg_color=COLOR_ACCENT,
                      hover_color=COLOR_ACCENT_HOVER, corner_radius=8, height=38, width=150,
                      font=(FONT_FAMILY, 12, "bold")).grid(row=8, column=0, sticky="w")

    def load(self, control_id=None):
        self.editing_id = control_id
        if control_id:
            row = next((c for c in fetch_controls() if c["control_id"] == control_id), None)
            self.title_label.configure(text="Modifier le contrôle")
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, row["control_name"])
            self.famille_entry.delete(0, "end")
            self.famille_entry.insert(0, row["famille"] or "")
            self.frequence_combo.set(row["frequence"] or "Journalier")
            self.description_text.delete("1.0", "end")
            self.description_text.insert("1.0", row["description"] or "")
        else:
            self.title_label.configure(text="Nouveau contrôle")
            self.name_entry.delete(0, "end")
            self.famille_entry.delete(0, "end")
            self.frequence_combo.set("Journalier")
            self.description_text.delete("1.0", "end")

    def _save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Attention", "Le nom du contrôle est obligatoire.")
            return
        famille = self.famille_entry.get().strip()
        frequence = self.frequence_combo.get()
        description = self.description_text.get("1.0", "end").strip()
        if self.editing_id:
            update_control(self.editing_id, name, famille, frequence, description)
        else:
            insert_control(next_control_id(), name, famille, frequence, description)
        self.app.navigate("catalogue")


# ============================================================
# Catégories : liste + page dédiée d'ajout
# ============================================================

class CategoriePage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLOR_BODY_BG)
        self.app = app
        self._build()

    def _build(self):
        PageHeader(self, "Catégories", "Catégories utilisées pour classer les résultats",
                   action_text="Ajouter", action_command=self.add
                   ).pack(fill="x", padx=24, pady=(20, 16))

        self.table = TableFrame(self, [("Catégorie", 300, "w")])
        self.table.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def refresh(self):
        self.table.clear()
        for i, r in enumerate(fetch_categories()):
            self.table.add_row(
                [r["category"]],
                actions=[("trash", COLOR_ERROR, lambda cid=r["id"]: self.delete(cid))],
                alt=(i % 2 == 1),
            )

    def add(self):
        self.app.navigate("categorie_form")

    def delete(self, cat_id):
        if confirm("Supprimer cette catégorie ?"):
            try:
                delete_category(cat_id)
                self.refresh()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erreur", "Cette catégorie est référencée par des logs ou détails existants.")


class CategorieFormPage(ctk.CTkFrame):
    """Page dédiée (pas de modale) pour ajouter une catégorie."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLOR_BODY_BG)
        self.app = app
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 16))
        BackButton(header, command=lambda: self.app.navigate("categories")).pack(side="left")
        ctk.CTkLabel(header, text="Nouvelle catégorie", font=(FONT_FAMILY, 18, "bold"),
                     text_color=COLOR_TEXT_PRIMARY).pack(side="left", padx=16)

        card = Card(self)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(padx=24, pady=24, anchor="w")

        ctk.CTkLabel(form, text="Nom de la catégorie", font=(FONT_FAMILY, 12),
                     text_color=COLOR_TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.name_entry = ctk.CTkEntry(form, width=340, corner_radius=8,
                                        border_color=COLOR_BORDER, fg_color="white")
        self.name_entry.grid(row=1, column=0, sticky="w", pady=(0, 20))

        ctk.CTkButton(form, text="Enregistrer", command=self._save, fg_color=COLOR_ACCENT,
                      hover_color=COLOR_ACCENT_HOVER, corner_radius=8, height=38, width=150,
                      font=(FONT_FAMILY, 12, "bold")).grid(row=2, column=0, sticky="w")

    def load(self):
        self.name_entry.delete(0, "end")

    def _save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Attention", "Le nom de la catégorie est obligatoire.")
            return
        insert_category(name)
        self.app.navigate("categories")


# ============================================================
# Page Résumés (Logs)
# ============================================================

class LogPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=COLOR_BODY_BG)
        self._build()

    def _build(self):
        PageHeader(self, "Résumés des contrôles", "Historique des exécutions de contrôle",
                   action_text="Ajouter", action_command=self.add
                   ).pack(fill="x", padx=24, pady=(20, 12))

        filters = ctk.CTkFrame(self, fg_color="transparent")
        filters.pack(fill="x", padx=24, pady=(0, 12))
        ctk.CTkLabel(filters, text="Du", font=(FONT_FAMILY, 11),
                     text_color=COLOR_TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        self.date_from = ctk.CTkEntry(filters, width=110, placeholder_text="AAAA-MM-JJ",
                                       corner_radius=8, border_color=COLOR_BORDER, fg_color="white")
        self.date_from.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(filters, text="Au", font=(FONT_FAMILY, 11),
                     text_color=COLOR_TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        self.date_to = ctk.CTkEntry(filters, width=110, placeholder_text="AAAA-MM-JJ",
                                     corner_radius=8, border_color=COLOR_BORDER, fg_color="white")
        self.date_to.pack(side="left", padx=(0, 10))
        self.severity_filter = ctk.CTkComboBox(filters, values=["Toutes", "OK", "ATTENTION", "CRITIQUE"],
                                                 width=130, corner_radius=8, border_color=COLOR_BORDER,
                                                 button_color=COLOR_ACCENT, fg_color="white", state="readonly")
        self.severity_filter.set("Toutes")
        self.severity_filter.pack(side="left", padx=(0, 10))
        ctk.CTkButton(filters, text="Filtrer", command=self.refresh, fg_color=COLOR_ACCENT,
                      hover_color=COLOR_ACCENT_HOVER, corner_radius=8, width=90).pack(side="left")

        columns = [
            ("Date", 90, "w"), ("Contrôle", 220, "w"), ("Catégorie", 90, "w"),
            ("Nb items", 70, "w"), ("Montant", 100, "w"), ("Sévérité", 100, "w"),
        ]
        self.table = TableFrame(self, columns)
        self.table.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def refresh(self):
        self.table.clear()
        rows = fetch_logs(
            self.date_from.get().strip() or None,
            self.date_to.get().strip() or None,
            self.severity_filter.get(),
        )
        for i, r in enumerate(rows):
            style = SEVERITY_STYLES.get(r["severite"], SEVERITY_STYLES[None])
            montant = f"{r['montant_impacte']:.2f}" if r["montant_impacte"] is not None else "-"
            self.table.add_row(
                [r["date_controle"], r["control_name"], r["category"], r["nb_items"], montant,
                 lambda parent, s=r["severite"], st=style: make_badge(parent, s, st["bg"], st["fg"])],
                actions=[("trash", COLOR_ERROR, lambda lid=r["id"]: self.delete(lid))],
                alt=(i % 2 == 1),
            )

    def add(self):
        controls = fetch_controls()
        categories = fetch_categories()
        if not controls or not categories:
            messagebox.showwarning("Attention", "Créez au moins un contrôle et une catégorie d'abord.")
            return
        control_map = {f"{r['control_id']} - {r['control_name']}": r["control_id"] for r in controls}
        category_map = {f"{r['id']} - {r['category']}": r["id"] for r in categories}

        dlg = FormDialog(self, "Nouveau résumé de contrôle", [
            ("Contrôle", "control", "combo", list(control_map.keys())),
            ("Catégorie (FK)", "category", "combo", list(category_map.keys())),
            ("Date (AAAA-MM-JJ)", "date_controle", "entry"),
            ("Catégorie (texte libre)", "categorie", "entry"),
            ("Nb items", "nb_items", "entry"),
            ("Montant impacté", "montant_impacte", "entry"),
            ("Sévérité", "severite", "combo", ["OK", "ATTENTION", "CRITIQUE"]),
        ], initial={"date_controle": date.today().isoformat(), "nb_items": "0"})

        if not dlg.result:
            return
        try:
            insert_log(
                control_map[dlg.result["control"]],
                category_map[dlg.result["category"]],
                dlg.result["date_controle"],
                dlg.result["categorie"] or "N/A",
                int(dlg.result["nb_items"] or 0),
                float(dlg.result["montant_impacte"]) if dlg.result["montant_impacte"] else None,
                dlg.result["severite"],
            )
            self.refresh()
        except (ValueError, sqlite3.IntegrityError) as e:
            messagebox.showerror("Erreur", f"Impossible d'enregistrer : {e}")

    def delete(self, log_id):
        if confirm("Supprimer ce résumé ?"):
            delete_log(log_id)
            self.refresh()


# ============================================================
# Page Détails
# ============================================================

class DetailPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=COLOR_BODY_BG)
        self._build()

    def _build(self):
        PageHeader(self, "Détails des contrôles", "Éléments détectés, ligne par ligne",
                   action_text="Ajouter", action_command=self.add
                   ).pack(fill="x", padx=24, pady=(20, 12))

        filters = ctk.CTkFrame(self, fg_color="transparent")
        filters.pack(fill="x", padx=24, pady=(0, 12))
        ctk.CTkLabel(filters, text="Contrôle ID", font=(FONT_FAMILY, 11),
                     text_color=COLOR_TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        self.control_filter = ctk.CTkEntry(filters, width=70, corner_radius=8,
                                            border_color=COLOR_BORDER, fg_color="white")
        self.control_filter.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(filters, text="Date", font=(FONT_FAMILY, 11),
                     text_color=COLOR_TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        self.date_filter = ctk.CTkEntry(filters, width=110, placeholder_text="AAAA-MM-JJ",
                                         corner_radius=8, border_color=COLOR_BORDER, fg_color="white")
        self.date_filter.pack(side="left", padx=(0, 10))
        ctk.CTkButton(filters, text="Filtrer", command=self.refresh, fg_color=COLOR_ACCENT,
                      hover_color=COLOR_ACCENT_HOVER, corner_radius=8, width=90).pack(side="left")

        columns = [
            ("Date", 90, "w"), ("Contrôle", 190, "w"), ("Clé métier", 120, "w"),
            ("Catégorie", 90, "w"), ("Détail", 220, "w"),
        ]
        self.table = TableFrame(self, columns)
        self.table.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def refresh(self):
        self.table.clear()
        rows = fetch_details(
            int(self.control_filter.get()) if self.control_filter.get().strip().isdigit() else None,
            self.date_filter.get().strip() or None,
        )
        for i, r in enumerate(rows):
            self.table.add_row(
                [r["date_controle"], r["control_name"], r["cle_metier"], r["categorie"], r["detail"]],
                actions=[("trash", COLOR_ERROR, lambda did=r["id"]: self.delete(did))],
                alt=(i % 2 == 1),
            )

    def add(self):
        controls = fetch_controls()
        categories = fetch_categories()
        if not controls or not categories:
            messagebox.showwarning("Attention", "Créez au moins un contrôle et une catégorie d'abord.")
            return
        control_map = {f"{r['control_id']} - {r['control_name']}": r["control_id"] for r in controls}
        category_map = {f"{r['id']} - {r['category']}": r["id"] for r in categories}

        dlg = FormDialog(self, "Nouveau détail", [
            ("Contrôle", "control", "combo", list(control_map.keys())),
            ("Catégorie (FK)", "category", "combo", list(category_map.keys())),
            ("Date (AAAA-MM-JJ)", "date_controle", "entry"),
            ("Clé métier", "cle_metier", "entry"),
            ("Catégorie (texte libre)", "categorie", "entry"),
            ("Détail", "detail", "text"),
        ], initial={"date_controle": date.today().isoformat()})

        if not dlg.result:
            return
        try:
            insert_detail(
                control_map[dlg.result["control"]],
                category_map[dlg.result["category"]],
                dlg.result["date_controle"],
                dlg.result["cle_metier"],
                dlg.result["categorie"] or "N/A",
                dlg.result["detail"],
            )
            self.refresh()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Erreur", f"Impossible d'enregistrer : {e}")

    def delete(self, detail_id):
        if confirm("Supprimer ce détail ?"):
            delete_detail(detail_id)
            self.refresh()


# ============================================================
# Application principale (sidebar + pages)
# ============================================================

class BillingFixControlApp(ctk.CTk):
    NAV_ITEMS = [
        ("dashboard", "Dashboard", "home"),
        ("catalogue", "Catalogue", "list"),
        ("categories", "Catégories", "tag"),
        ("logs", "Résumés", "chart"),
        ("details", "Détails", "search"),
    ]
    PAGE_PARENT = {"catalogue_form": "catalogue", "categorie_form": "categories"}

    def __init__(self):
        super().__init__()
        _resolve_font(self)

        self.title("BillingFixControl")
        self.geometry("1300x800")
        self.configure(fg_color=COLOR_BODY_BG)

        create_database()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ctk.CTkFrame(self, fg_color=COLOR_SIDEBAR_BG, width=230, corner_radius=0, border_width=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        logo_box = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_box.pack(fill="x", padx=20, pady=(24, 30))
        ctk.CTkLabel(logo_box, text="BillingFixControl", font=(FONT_FAMILY, 16, "bold"),
                     text_color=COLOR_TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(logo_box, text="Revenue Assurance", font=(FONT_FAMILY, 10),
                     text_color=COLOR_TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))

        footer_box = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer_box.pack(side="bottom", fill="x", padx=20, pady=(10, 20))

        ctk.CTkLabel(
            footer_box,
            text="RAFMcopyright©yas2026",
            font=(FONT_FAMILY, 9),
            text_color=COLOR_TEXT_SECONDARY
        ).pack(anchor="w")

        self._icon_names = {key: icon for key, _, icon in self.NAV_ITEMS}
        self.nav_buttons = {}
        for key, label, icon_name in self.NAV_ITEMS:
            btn = ctk.CTkButton(
                sidebar, text=f"  {label}", image=get_icon(icon_name, 17, COLOR_TEXT_SECONDARY),
                compound="left", anchor="w", font=(FONT_FAMILY, 13),
                fg_color="transparent", text_color=COLOR_TEXT_SECONDARY,
                hover_color=COLOR_ACCENT_LIGHT, corner_radius=8, height=40,
                command=lambda k=key: self.navigate(k),
            )
            btn.pack(fill="x", padx=14, pady=3)
            self.nav_buttons[key] = btn

        # Content area
        content = ctk.CTkFrame(self, fg_color=COLOR_BODY_BG, corner_radius=0)
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        self.pages = {
            "dashboard": DashboardPage(content),
            "catalogue": CataloguePage(content, self),
            "catalogue_form": CatalogueFormPage(content, self),
            "categories": CategoriePage(content, self),
            "categorie_form": CategorieFormPage(content, self),
            "logs": LogPage(content),
            "details": DetailPage(content),
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.navigate("dashboard")

    def navigate(self, key, **kwargs):
        parent_key = self.PAGE_PARENT.get(key, key)
        for k, btn in self.nav_buttons.items():
            active = k == parent_key
            btn.configure(
                fg_color=COLOR_ACCENT_LIGHT if active else "transparent",
                text_color=COLOR_ACCENT if active else COLOR_TEXT_SECONDARY,
                image=get_icon(self._icon_names[k], 17, COLOR_ACCENT if active else COLOR_TEXT_SECONDARY),
            )
        page = self.pages[key]
        if hasattr(page, "load"):
            page.load(**kwargs)
        else:
            page.refresh()
        page.tkraise()


if __name__ == "__main__":
    app = BillingFixControlApp()
    app.mainloop()