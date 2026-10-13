from collections.abc import Mapping
from datetime import date, datetime, timedelta

from db import fetch_all, fetch_one

TABLE = "revenu_yas_wifi"
LOOKBACK_DAYS = 90


def _to_date(v):
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    return datetime.strptime(str(v)[:10], "%Y-%m-%d").date()


def _num(v, cast):
    return None if v is None else cast(v)      # gère aussi les Decimal


def _first_value(row):
    if row is None:
        return None
    return next(iter(row.values())) if isinstance(row, Mapping) else row[0]


def _normalize(r):
    """Accepte une ligne sous forme de dict ou de tuple/liste (selon votre module db)."""
    if isinstance(r, Mapping):
        day, nl, up, tr = r["day"], r["number_lines"], r["unit_price"], r["total_revenue"]
    else:
        day, nl, up, tr = r[0], r[1], r[2], r[3]
    return {"day": _to_date(day), "number_lines": _num(nl, int),
            "unit_price": _num(up, float), "total_revenue": _num(tr, float)}


class YasWifiRepository:

    def get_latest_date(self):
        """Dernier jour présent dans la table (None si la table est vide)."""
        value = _first_value(fetch_one(f"SELECT MAX(day) FROM {TABLE}"))
        return None if value is None else _to_date(value)

    def get_wifi_report(self, date_controle=None, lookback_days=LOOKBACK_DAYS):
        """
        Lignes de la table jusqu'au jour contrôlé inclus, sur `lookback_days` jours.
        date_controle : jour contrôlé (par défaut : la veille).
        Renvoie une liste de dict {day, number_lines, unit_price, total_revenue}, triée par jour.
        """
        if date_controle is None:
            date_controle = date.today() - timedelta(days=1)
        start = date_controle - timedelta(days=lookback_days)
        end = date_controle + timedelta(days=1)          # borne exclue : sûr pour DATE et TIMESTAMP

        # Les dates viennent d'objets `date` (jamais d'une saisie libre) : pas de risque d'injection.
        rows = fetch_all(f"""
            SELECT day, number_lines, unit_price, total_revenue
            FROM {TABLE}
            WHERE day >= '{start:%Y-%m-%d}' AND day < '{end:%Y-%m-%d}'
            ORDER BY day
        """)
        return [_normalize(r) for r in (rows or [])]