"""
Calcul du rapport YAS WiFi à partir des lignes de la table `revenu_yas_wifi`.

Fonction pure (aucune dépendance à tkinter ni à la base) : elle prend les lignes
renvoyées par le repository et produit le dictionnaire attendu par WifiDashboard.
Elle est donc testable seule (voir tests/test_wifi_report.py).
"""
from collections import defaultdict
from datetime import date, timedelta
from statistics import median

EXPECTED_PRICE = 250     # prix unitaire attendu (FCFA)
THRESHOLD = 30           # alerte si le revenu de la veille s'écarte de plus de 30 % de la moyenne 7 jours
LOW_RATIO = 0.5          # "jour anormalement bas" : < 50 % de la médiane (même règle que le rapport Excel)


def default_control_date(today=None):
    """Jour contrôlé par défaut : la veille."""
    return (today or date.today()) - timedelta(days=1)


def _clean(x):
    """105250.0 -> 105250 (affichage propre), sinon valeur inchangée."""
    if x is None:
        return 0
    x = float(x)
    return int(x) if x.is_integer() else x


def _d(day):
    return day.strftime("%d/%m/%Y")


def build_report(rows, date_controle, expected_price=EXPECTED_PRICE,
                 threshold=THRESHOLD, low_ratio=LOW_RATIO):
    """
    rows : liste de dict {"day": date, "number_lines": int, "unit_price": float, "total_revenue": float}
    date_controle : jour contrôlé (la veille). Les contrôles portent sur ce jour.
    """
    if not rows:
        raise ValueError("Aucune donnée dans la table sur la période demandée.")

    veille = date_controle
    rev_by_day, lines_by_day = defaultdict(float), defaultdict(float)
    for r in rows:
        rev_by_day[r["day"]] += r["total_revenue"] or 0
        lines_by_day[r["day"]] += r["number_lines"] or 0
    present = sorted(rev_by_day)
    first_day, last_day = present[0], present[-1]

    # ---------------------------------------------------------- 7 contrôles
    retard = max(0, (veille - last_day).days)
    manquants = (max(last_day, veille) - first_day).days + 1 - len(present)
    doublons = len(rows) - len(present)
    ecarts = sum(1 for r in rows
                 if None not in (r["number_lines"], r["unit_price"], r["total_revenue"])
                 and abs(r["number_lines"] * r["unit_price"] - r["total_revenue"]) > 0.005)
    hors_prix = sum(1 for r in rows
                    if r["unit_price"] is not None and abs(r["unit_price"] - expected_price) > 1e-9)
    invalides = sum(1 for r in rows
                    if r["number_lines"] is None or r["total_revenue"] is None
                    or r["number_lines"] < 0 or r["total_revenue"] < 0)

    window = [rev_by_day[d] for d in present if veille - timedelta(days=7) <= d < veille]
    variation = None
    if window and sum(window) != 0:
        variation = (rev_by_day.get(veille, 0) / (sum(window) / len(window)) - 1) * 100
    var_ok = variation is not None and abs(variation) <= threshold
    var_txt = "n/d" if variation is None else f"{variation:+.1f}%".replace(".", ",")

    checks = [
        ("Données de la veille présentes (retard en jours)", str(retard), "0", retard == 0),
        ("Aucun jour manquant (nombre de jours)", str(manquants), "0", manquants == 0),
        ("Aucun doublon de jour (nombre)", str(doublons), "0", doublons == 0),
        ("Nbre Numéro × prix = revenu (nombre d'écarts)", str(ecarts), "0", ecarts == 0),
        ("Prix unitaire conforme (Numéros hors prix attendu)", str(hors_prix), "0", hors_prix == 0),
        ("Aucune valeur vide ou négative (nombre)", str(invalides), "0", invalides == 0),
        ("Revenu de la veille cohérent vs moyenne 7 jours", var_txt, f"±{threshold}%", var_ok),
    ]

    # ---------------------------------------------------------- séries des graphiques
    # calendrier continu : un jour manquant apparaît à 0 (visible), au lieu d'être masqué
    end = max(last_day, veille)
    calendar = [first_day + timedelta(days=i) for i in range((end - first_day).days + 1)]
    revenue = [_clean(rev_by_day.get(d, 0)) for d in calendar]
    numbers = [_clean(lines_by_day.get(d, 0)) for d in calendar]
    cumul, run = [], 0
    for v in revenue:
        run += v
        cumul.append(run)

    total = sum(rev_by_day.values())
    total_numbers = sum(lines_by_day.values())

    # ---------------------------------------------------------- repères
    med = median(rev_by_day[d] for d in present)
    low_days = [d for d in present if rev_by_day[d] < low_ratio * med]
    low = low_days[0] if low_days else None

    return {
        "days": [d.strftime("%d/%m") for d in calendar],
        "revenue": revenue, "numbers": numbers, "cumul": cumul,
        "total": _clean(total), "total_numbers": _clean(total_numbers),
        "avg_day": total / len(present), "avg_numbers": total_numbers / len(present),
        "last": _clean(rev_by_day.get(veille, 0)),
        "last_numbers": _clean(lines_by_day.get(veille, 0)),
        "variation": 0.0 if variation is None else variation,
        "threshold": threshold,
        "checks": checks, "median": _clean(med),
        "first_day": _d(first_day), "last_day": _d(last_day), "checked_day": _d(veille),
        "low_count": len(low_days),
        "low_day": _d(low) if low else "—",
        "low_lines": _clean(lines_by_day[low]) if low else 0,
        "low_revenue": _clean(rev_by_day[low]) if low else 0,
        "low_idx": calendar.index(low) if low else None,
        # La table ne contient aucune zone géographique : on n'invente rien.
        "zones": [],
    }
