from datetime import date
from repositories.control_repository import ControlRepository
from models import ControlCard


class DashboardService:
    def __init__(self, repository=None):
        self.repository = repository or ControlRepository()

    def load_cardsOld(self, date_controle=None):
        rows = self.repository.get_dashboard(date_controle)
        return [ControlCard(**row) for row in rows]

    def load_cards(self,date_controle=None,perimetre="FXL",mode_execution="COMMIT"):

        rows = self.repository.get_dashboard(
            date_controle,
            perimetre,
            mode_execution
        )

        return [
            ControlCard(**row)
            for row in rows
        ]

    @staticmethod
    def counters(cards):
        return {
            "total": len(cards),
            "critical": sum(c.severite == "CRITIQUE" for c in cards),
            "attention": sum(c.severite == "ATTENTION" for c in cards),
            "ok": sum(c.severite == "OK" for c in cards),
        }
