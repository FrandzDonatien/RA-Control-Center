import sqlite3
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "billingfixcontrol.db"


# ============================================================
# Connexion à la base
# ============================================================

def get_connection():
    """
    Retourne une connexion à la base SQLite.
    """
    conn = sqlite3.connect(DATABASE_PATH)

    # Permet d'accéder aux colonnes par leur nom
    conn.row_factory = sqlite3.Row

    # Active les clés étrangères
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# ============================================================
# Création de la base de données
# ============================================================

def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # ----------------------------------------------------
        # 1. Catalogue des contrôles
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ra_controls_catalog (
                control_id INTEGER PRIMARY KEY,
                control_name TEXT NOT NULL,
                famille TEXT,
                frequence TEXT,
                description TEXT
            )
        """)

        # ----------------------------------------------------
        # 2. Catégories des contrôles
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ra_controls_catalog_category (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL
            )
        """)

        # ----------------------------------------------------
        # 3. Insertion des catégories
        # ----------------------------------------------------

        cursor.executemany("""
            INSERT OR IGNORE INTO ra_controls_catalog_category
            (id, category)
            VALUES (?, ?)
        """, [
            (1, "FXL"),
            (2, "HYB")
        ])

        # ----------------------------------------------------
        # 4. Insertion du catalogue des contrôles
        # ----------------------------------------------------

        controls = [

            (
                1,
                "Clients actifs vs run de facturation",
                "Population",
                "Journalier",
                "Verifie que tous les actifs postpaid sont factures"
            ),

            (
                2,
                "Reconciliation entre cycles consecutifs",
                "Population",
                "Mensuel",
                "Detecte les abonnes disparus d'un cycle a l'autre"
            ),

            (
                3,
                "Validation des calculs de facturation",
                "Exactitude",
                "Mensuel",
                "Recalcul independant des montants factures"
            ),

            (
                4,
                "Analyse de variance mois/mois",
                "Exactitude",
                "Mensuel",
                "Suivi ARPU, revenu, nb abonnes"
            ),

            (
                5,
                "Validation du prorata",
                "Exactitude",
                "Journalier",
                "Controle des factures au prorata"
            ),

            (
                6,
                "Facturation a 0 / hors seuils",
                "Exactitude",
                "Journalier",
                "Detection des prix aberrants"
            ),

            (
                7,
                "Montant minimum du plan",
                "Exactitude",
                "Journalier",
                "Verifie le respect du minimum facturable"
            ),

            (
                8,
                "Frais uniques",
                "Charges specifiques",
                "Journalier",
                "Installation, penalites, reconnexion"
            ),

            (
                9,
                "Usage vs facturation",
                "Charges specifiques",
                "Journalier",
                "Voix, data, SMS, roaming, VAS"
            ),

            (
                10,
                "Promotions expirees",
                "Charges specifiques",
                "Journalier",
                "Remises appliquees au-dela de leur validite"
            ),

            (
                11,
                "Revue echantillon de factures",
                "Revue qualitative",
                "Mensuel",
                "Revue manuelle documentee"
            ),

            (
                12,
                "Analyse de marge / revenue assurance",
                "Revue qualitative",
                "Mensuel",
                "Cout de service vs revenu facture"
            )
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO ra_controls_catalog
            (
                control_id,
                control_name,
                famille,
                frequence,
                description
            )
            VALUES (?, ?, ?, ?, ?)
        """, controls)

        # ----------------------------------------------------
        # 5. Log résumé
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ra_controls_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                control_id INTEGER NOT NULL,

                catalog_category_id INTEGER NOT NULL,

                date_controle DATE NOT NULL,

                categorie TEXT NOT NULL,

                nb_items INTEGER NOT NULL DEFAULT 0,

                montant_impacte REAL,

                severite TEXT NOT NULL
                    CHECK (
                        severite IN (
                            'OK',
                            'ATTENTION',
                            'CRITIQUE'
                        )
                    ),

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                UNIQUE (
                    control_id,
                    date_controle,
                    categorie
                ),

                FOREIGN KEY (control_id)
                    REFERENCES ra_controls_catalog(control_id),

                FOREIGN KEY (catalog_category_id)
                    REFERENCES ra_controls_catalog_category(id)
            )
        """)

        # ----------------------------------------------------
        # 6. Log détail
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ra_controls_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                control_id INTEGER NOT NULL,

                catalog_category_id INTEGER NOT NULL,

                date_controle DATE NOT NULL,

                cle_metier TEXT NOT NULL,

                categorie TEXT NOT NULL,

                detail TEXT NOT NULL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (control_id)
                    REFERENCES ra_controls_catalog(control_id),

                FOREIGN KEY (catalog_category_id)
                    REFERENCES ra_controls_catalog_category(id)
            )
        """)

        # ----------------------------------------------------
        # 7. Index
        # ----------------------------------------------------

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ra_controls_log_date
            ON ra_controls_log (date_controle)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ra_controls_details_date
            ON ra_controls_details (control_id, date_controle)
        """)

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        conn.commit()

        print("Base de données créée avec succès.")
        print(f"Base : {DATABASE_PATH}")

    except Exception as e:

        conn.rollback()

        print("Erreur lors de la création de la base :")
        print(e)

        raise

    finally:

        conn.close()


# ============================================================
# Exécution directe
# ============================================================

if __name__ == "__main__":
    create_database()