# RA Tkinter Dashboard

Interface desktop Python/Tkinter inspirée du dashboard fourni :
- registre des 12 contrôles Revenue Assurance ;
- filtres par famille ;
- indicateurs globaux OK / ATTENTION / CRITIQUE ;
- cartes cliquables ;
- fenêtre de détail ;
- tableau JSONB des anomalies ;
- tendance des 7 dernières exécutions ;
- connexion PostgreSQL via `psycopg2`.

## 1. Installation

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
```

## 2. Configuration PostgreSQL

Copier `.env.example` en `.env` puis renseigner :

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=radb
DB_USER=postgres
DB_PASSWORD=mon_mot_de_passe
DEMO_MODE=false
```

## 3. Préparer la base

Exécuter `sql/schema.sql` dans RADB/PostgreSQL.

Ensuite les jobs RA alimentent :
- `ra_controls_catalog` : référentiel des contrôles ;
- `ra_controls_log` : résumé par date/catégorie ;
- `ra_controls_details` : détails métier en JSONB.

## 4. Tester l'interface sans base

Dans `.env` :

```env
DEMO_MODE=true
```

Puis :

```bash
python app.py
```

Le dashboard affichera les données de démonstration et le contrôle CTRL-02 dispose d'un exemple de détail similaire à votre capture.

## 5. Architecture

```text
ra_tkinter_dashboard/
│
├── app.py
├── config.py
├── db.py
├── models.py
├── requirements.txt
├── .env.example
├── README.md
│
├── repositories/
│   └── control_repository.py
│
├── services/
│   ├── dashboard_service.py
│   └── demo_data.py
│
├── ui/
│   ├── dashboard.py
│   ├── widgets.py
│   ├── detail_modal.py
│   ├── trend.py
│   └── theme.py
│
└── sql/
    └── schema.sql
```

## 6. Flux applicatif

```text
PostgreSQL
   │
   ▼
ControlRepository
   │
   ▼
DashboardService
   │
   ├── compteurs
   ├── cartes
   └── détails/tendances
   │
   ▼
Tkinter Dashboard
   │
   └── clic sur carte
          │
          ▼
      DetailModal
          ├── détails JSONB
          └── tendance 7 jours
```

## 7. Évolution recommandée

Pour la version suivante, ajouter :
- sélection d'une date d'exécution ;
- recherche par `service_id` / `msisdn` ;
- export Excel/CSV ;
- bouton « Relancer le contrôle » ;
- statut de dernière exécution ;
- montant impacté dans les cartes ;
- pagination du détail ;
- authentification ;
- journalisation des actions utilisateur ;
- connexion à vos procédures/jobs RA.
