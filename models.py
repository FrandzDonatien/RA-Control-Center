from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Control:
    control_id: int
    control_name: str
    famille: str
    frequence: str
    description: str = ""


@dataclass
class ControlCard:
    control_id: int
    control_name: str
    famille: str
    frequence: str
    description: str
    nb_items: int
    severite: str
    montant_impacte: Optional[float]
    date_controle: Optional[date]


@dataclass
class DetailRow:
    cle_metier: str
    categorie: str
    detail: dict
    date_controle: date
