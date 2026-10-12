"""Points de détail (quartiers / sites) par ville.

SPOTS : ville -> [(nom, longitude, latitude, poids)]
Coordonnées APPROXIMATIVES : à corriger avec vos vrais points,
ou à remplacer par une requête sur votre table de recharges.
"""

SPOTS = {
    "Lomé": [
        ("Bè", 1.2400, 6.1380, 0.20), ("Tokoin", 1.2200, 6.1550, 0.16),
        ("Adidogomé", 1.1800, 6.1750, 0.14), ("Agoè", 1.2150, 6.2300, 0.15),
        ("Baguida", 1.3300, 6.1850, 0.08), ("Hédzranawoé", 1.2000, 6.1900, 0.10),
        ("Port / Centre", 1.2850, 6.1300, 0.17),
    ],
    "Kara": [
        ("Centre-ville", 1.1860, 9.5510, 0.45), ("Kpéwa", 1.2050, 9.5700, 0.20),
        ("Tomdè", 1.1700, 9.5300, 0.20), ("Université", 1.2200, 9.5900, 0.15),
    ],
    "Sokodé": [
        ("Centre-ville", 1.1330, 8.9830, 0.50), ("Komah", 1.1500, 8.9650, 0.25),
        ("Kpangalam", 1.1100, 9.0000, 0.25),
    ],
    "Kpalimé": [
        ("Centre-ville", 0.6330, 6.9000, 0.60), ("Kpadapé", 0.6500, 6.9150, 0.40),
    ],
    "Atakpamé": [
        ("Centre-ville", 1.1330, 7.5300, 0.60), ("Kpodzi", 1.1500, 7.5500, 0.40),
    ],
}


def make_spots(zone):
    """Répartit le montant d'une zone sur ses points de détail (démo)."""
    raw = SPOTS.get(zone["name"])
    if not raw:
        return []
    total = sum(r[3] for r in raw)
    return [{
        "name": n, "lon": lo, "lat": la,
        "amount": zone["amount"] * p / total,
        "recharges": round(zone["recharges"] * p / total),
    } for n, lo, la, p in raw]