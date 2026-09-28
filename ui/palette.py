"""Palette claire partagée (inspirée de TailAdmin) pour tout le module FIXE."""

COLORS = {
    "bg":           "#F9FAFB",
    "panel":        "#FFFFFF",
    "panel_2":      "#F2F4F7",
    "track":        "#EAECF0",
    "border":       "#E4E7EC",
    "text":         "#1D2939",
    "text_soft":    "#344054",
    "muted":        "#667085",
    "accent":       "#465FFF",
    "accent_dark":  "#3641F5",
    "accent_soft":  "#ECF3FF",
    "white":        "#FFFFFF",
    "critical":     "#D92D20",
    "critical_bg":  "#FEF3F2",
    "attention":    "#DC6803",
    "attention_bg": "#FFFAEB",
    "ok":           "#039855",
    "ok_bg":        "#ECFDF3",
}

FONT = "Segoe UI"
MONO = "Consolas"

# sévérité -> (couleur du texte, couleur de fond)
SEVERITY_COLORS = {
    "CRITIQUE":  (COLORS["critical"], COLORS["critical_bg"]),
    "ATTENTION": (COLORS["attention"], COLORS["attention_bg"]),
    "OK":        (COLORS["ok"], COLORS["ok_bg"]),
    "N/A":       (COLORS["muted"], COLORS["panel_2"]),
}

# sévérité -> nom d'icône
SEVERITY_ICONS = {
    "CRITIQUE": "alert",
    "ATTENTION": "warning",
    "OK": "check_circle",
    "N/A": "warning",
}