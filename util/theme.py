"""Palette (inspirée de TailAdmin) et helpers partagés par les écrans."""

T = {
    "bg": "#F9FAFB",
    "card": "#FFFFFF",
    "border": "#E4E7EC",
    "gray50": "#F9FAFB",
    "gray100": "#F2F4F7",
    "gray300": "#D0D5DD",
    "text": "#101828",
    "text_soft": "#344054",
    "muted": "#667085",
    "brand": "#465FFF",
    "brand_dark": "#3641F5",
    "brand_50": "#ECF3FF",
    "brand_200": "#C2D6FF",
    "brand_300": "#9CB9FF",
    "ok": "#12B76A",
    "ok_text": "#027A48",
    "ok_50": "#ECFDF3",
    "ok_200": "#ABEFC6",
    "err": "#F04438",
    "err_text": "#B42318",
    "err_50": "#FEF3F2",
    "err_200": "#FECDCA",
    "warn": "#F79009",
    "warn_text": "#B54708",
    "warn_50": "#FFFAEB",
}


def fmt(value, decimals=0):
    """1480500 -> '1 480 500'"""
    return f"{value:,.{decimals}f}".replace(",", " ")