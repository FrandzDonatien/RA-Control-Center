import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

APP_TITLE = "Registre des contrôles — Revenue Assurance"
APP_WIDTH = 1700
APP_HEIGHT = 900

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "radb"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# Permet de lancer l'interface sans PostgreSQL pour tester l'UI.
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

COLORS = {
    "bg": "#121316",
    "panel": "#1d1f26",
    "panel_2": "#20232b",
    "border": "#30343d",
    "text": "#f2f2f2",
    "muted": "#858b96",
    "critical": "#f06a5f",
    "critical_bg": "#351d1b",
    "attention": "#f0b62d",
    "attention_bg": "#332b12",
    "ok": "#66c58a",
    "ok_bg": "#163020",
    "white": "#ffffff",
    "accent": "#6d8cff",
}
