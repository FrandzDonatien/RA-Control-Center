-- Schéma unifié Revenue Assurance
-- Exécuter ce fichier dans la base RADB/PostgreSQL.

CREATE TABLE IF NOT EXISTS ra_controls_catalog (
    control_id      smallint PRIMARY KEY,
    control_name    text NOT NULL,
    famille         text,
    frequence       text,
    description     text
);

INSERT INTO ra_controls_catalog
(control_id, control_name, famille, frequence, description) VALUES
(1,  'Clients actifs vs run de facturation',        'Population',           'Journalier', 'Vérifie que tous les actifs postpaid sont facturés'),
(2,  'Réconciliation entre cycles consécutifs',    'Population',           'Journalier', 'Détecte les abonnés disparus d''un cycle à l''autre'),
(3,  'Validation des calculs de facturation',      'Exactitude',           'Mensuel',    'Recalcul indépendant des montants facturés'),
(4,  'Analyse de variance mois/mois',              'Exactitude',           'Mensuel',    'Suivi ARPU, revenu, nb abonnés'),
(5,  'Validation du prorata',                      'Exactitude',           'Journalier', 'Contrôle des factures au prorata'),
(6,  'Facturation à 0 / hors seuils',              'Exactitude',           'Journalier', 'Détection des prix aberrants'),
(7,  'Montant minimum du plan',                    'Exactitude',           'Journalier', 'Vérifie le respect du minimum facturable'),
(8,  'Frais uniques',                              'Charges spécifiques',  'Journalier', 'Installation, pénalités, reconnexion'),
(9,  'Usage vs facturation',                       'Charges spécifiques',  'Journalier', 'Voix, data, SMS, roaming, VAS'),
(10, 'Promotions expirées',                        'Charges spécifiques',  'Journalier', 'Remises appliquées au-delà de leur validité'),
(11, 'Revue d''échantillon de factures',           'Revue qualitative',    'Mensuel',    'Revue manuelle documentée'),
(12, 'Analyse de marge / revenue assurance',       'Revue qualitative',    'Mensuel',    'Coût de service vs revenu facturé')
ON CONFLICT (control_id) DO NOTHING;

CREATE TABLE IF NOT EXISTS ra_controls_log (
    id                  bigserial PRIMARY KEY,
    control_id          smallint NOT NULL REFERENCES ra_controls_catalog(control_id),
    date_controle       date NOT NULL,
    categorie           text NOT NULL,
    nb_items            integer NOT NULL DEFAULT 0,
    montant_impacte     numeric,
    severite            text NOT NULL CHECK (severite IN ('OK','ATTENTION','CRITIQUE')),
    created_at          timestamp DEFAULT now(),
    UNIQUE (control_id, date_controle, categorie)
);

CREATE TABLE IF NOT EXISTS ra_controls_details (
    id                  bigserial PRIMARY KEY,
    control_id          smallint NOT NULL REFERENCES ra_controls_catalog(control_id),
    date_controle       date NOT NULL,
    cle_metier          text NOT NULL,
    categorie           text NOT NULL,
    detail              jsonb NOT NULL,
    created_at          timestamp DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ra_controls_log_date
    ON ra_controls_log (date_controle);

CREATE INDEX IF NOT EXISTS idx_ra_controls_details_date
    ON ra_controls_details (control_id, date_controle);

ALTER TABLE ra_controls_log
ADD COLUMN IF NOT EXISTS perimetre text
    CHECK (perimetre IN ('FXL', 'HYB'));

ALTER TABLE ra_controls_log
ADD COLUMN IF NOT EXISTS mode_execution text
    CHECK (mode_execution IN ('COMMIT', 'SIMULATION'));

CREATE INDEX IF NOT EXISTS idx_ra_controls_log_filters
ON ra_controls_log (
    date_controle,
    perimetre,
    mode_execution
);