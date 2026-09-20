from datetime import date, timedelta
import random


CATALOG = [
    (1, "Clients actifs vs run de facturation", "Population", "Journalier", "Vérifie que tous les actifs postpaid sont facturés"),
    (2, "Réconciliation entre cycles consécutifs", "Population", "Journalier", "Détecte les abonnés disparus d'un cycle à l'autre"),
    (3, "Validation des calculs de facturation", "Exactitude", "Mensuel", "Recalcul indépendant des montants facturés"),
    (4, "Analyse de variance mois/mois", "Exactitude", "Mensuel", "Suivi ARPU, revenu, nb abonnés"),
    (5, "Validation du prorata", "Exactitude", "Journalier", "Contrôle des factures au prorata"),
    (6, "Facturation à 0 / hors seuils", "Exactitude", "Journalier", "Détection des prix aberrants"),
    (7, "Montant minimum du plan", "Exactitude", "Journalier", "Vérifie le respect du minimum facturable"),
    (8, "Frais uniques", "Charges spécifiques", "Journalier", "Installation, pénalités, reconnexion"),
    (9, "Usage vs facturation", "Charges spécifiques", "Journalier", "Voix, data, SMS, roaming, VAS"),
    (10, "Promotions expirées", "Charges spécifiques", "Journalier", "Remises appliquées au-delà de leur validité"),
    (11, "Revue d'échantillon de factures", "Revue qualitative", "Mensuel", "Revue manuelle documentée"),
    (12, "Analyse de marge / revenue assurance", "Revue qualitative", "Mensuel", "Coût de service vs revenu facturé"),
]

VALUES = [14, 7, 0, 1, 2, 9, 0, 5, 92, 23, 0, 3]
SEVERITIES = ["CRITIQUE", "ATTENTION", "OK", "ATTENTION", "OK", "CRITIQUE",
              "OK", "ATTENTION", "CRITIQUE", "ATTENTION", "OK", "ATTENTION"]


class DemoRepository:
    def __init__(self):
        self.latest = date(2026, 9, 18)

    def get_dashboardOld(self, date_controle=None):
        d = date_controle or self.latest
        result = []
        for item, value, sev in zip(CATALOG, VALUES, SEVERITIES):
            cid, name, family, freq, desc = item
            result.append({
                "control_id": cid, "control_name": name, "famille": family,
                "frequence": freq, "description": desc, "nb_items": value,
                "severite": sev, "montant_impacte": None, "date_controle": d
            })
        return result

    def get_dashboard(
    self,
    date_controle=None,
    perimetre="FXL",
    mode_execution="COMMIT"
):

        d = date_controle or self.latest

        result = []

        multiplier = 1

        if perimetre == "HYB":
            multiplier = 0.7

        if mode_execution == "SIMULATION":
            multiplier = 0.85

        for item, value, sev in zip(
            CATALOG,
            VALUES,
            SEVERITIES
        ):

            cid, name, family, freq, desc = item

            result.append({
                "control_id": cid,
                "control_name": name,
                "famille": family,
                "frequence": freq,
                "description": desc,

                "nb_items": int(
                    value * multiplier
                ),

                "severite": sev,

                "montant_impacte": None,

                "date_controle": d
            })

        return result

    def get_latest_date(self,perimetre="FXL",mode_execution="COMMIT"):
        return self.latest

    def get_details(self, control_id, date_controle):
        if control_id == 2:
            return [
                {"cle_metier": "77011230", "categorie": "ANOMALIE NOUVELLE",
                 "detail": {"montant_ttc_n_1": 74500, "statut_actuel": None},
                 "date_controle": date_controle},
                {"cle_metier": "77099821", "categorie": "ANOMALIE NOUVELLE",
                 "detail": {"montant_ttc_n_1": 61200, "statut_actuel": None},
                 "date_controle": date_controle},
                {"cle_metier": "77055120", "categorie": "ANOMALIE NOUVELLE",
                 "detail": {"montant_ttc_n_1": 48900, "statut_actuel": None},
                 "date_controle": date_controle},
            ]
        return [
            {"cle_metier": f"ITEM-{i:03d}", "categorie": "ANOMALIE",
             "detail": {"exemple": "Détail métier disponible depuis JSONB"},
             "date_controle": date_controle}
            for i in range(1, min(6, VALUES[control_id - 1] + 1))
        ]

    def get_log_summary(self, control_id, date_controle):
        return [{"categorie": "ANOMALIE", "nb_items": VALUES[control_id-1],
                 "montant_impacte": None, "severite": SEVERITIES[control_id-1]}]

    def get_trend(self, control_id, date_controle, limit=7):
        base = VALUES[control_id - 1]
        out = []
        for i in range(limit - 1, -1, -1):
            d = date_controle - timedelta(days=i)
            value = max(0, int(base + random.randint(-3, 3)))
            out.append({"date_controle": d, "nb_items": value})
        return out
