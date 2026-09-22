from db import fetch_all, fetch_one
 
 
class ControlRepository:
    def get_catalog(self):
        return fetch_all("""
            SELECT control_id, control_name, famille, frequence, description
            FROM ra_controls_catalog
            ORDER BY control_id
        """)
 
    def get_latest_dateOld(self):
        row = fetch_one("""
            SELECT MAX(date_controle) AS latest_date
            FROM ra_controls_log
        """)
        return row["latest_date"] if row else None
 
    def get_latest_date(self,perimetre="FXL",mode_execution="COMMIT"):
 
        row = fetch_one("""
            SELECT MAX(l.date_controle) AS latest_date
            FROM ra_controls_log l
            JOIN ra_controls_catalog_category cc
                ON cc.id = l.catalog_category_id
            AND cc.category = %s
            JOIN ra_controls_catalog_mode_execution me
            ON me.id = l.mode_execution
           AND me.mode_execution = %s
        """, (
            perimetre,
            mode_execution
        ))
 
        return row["latest_date"] if row else None
 
    def get_dashboardOld(self, date_controle=None):
        if date_controle is None:
            date_controle = self.get_latest_date()
 
        if date_controle is None:
            return []
 
        return fetch_all("""
            WITH ranked AS (
                SELECT
                    l.*,
                    ROW_NUMBER() OVER (
                        PARTITION BY l.control_id
                        ORDER BY
                            CASE l.severite
                                WHEN 'CRITIQUE' THEN 3
                                WHEN 'ATTENTION' THEN 2
                                ELSE 1
                            END DESC,
                            l.nb_items DESC
                    ) AS rn
                FROM ra_controls_log l
                WHERE l.date_controle = %s
            )
            SELECT
                c.control_id,
                c.control_name,
                c.famille,
                c.frequence,
                c.description,
                COALESCE(r.nb_items, 0) AS nb_items,
                COALESCE(r.severite, 'OK') AS severite,
                r.montant_impacte,
                r.date_controle
            FROM ra_controls_catalog c
            LEFT JOIN ranked r
                ON r.control_id = c.control_id AND r.rn = 1
            ORDER BY c.control_id
        """, (date_controle,))
 
    def get_dashboard(self,date_controle=None,perimetre="FXL",mode_execution="COMMIT"):
 
        if date_controle is None:
            date_controle = self.get_latest_date(
                perimetre,
                mode_execution
            )
 
        if date_controle is None:
            return []
 
        return fetch_all("""
            WITH ranked AS (
                SELECT
                    l.*,
 
                    ROW_NUMBER() OVER (
                        PARTITION BY l.control_id
                        ORDER BY
                            CASE l.severite
                                WHEN 'CRITIQUE' THEN 3
                                WHEN 'ATTENTION' THEN 2
                                ELSE 1
                            END DESC,
                            l.nb_items DESC
                    ) AS rn
 
                FROM ra_controls_log l
 
                WHERE l.date_controle = %s
 
                AND l.catalog_category_id =(SELECT id FROM ra_controls_catalog_category WHERE category = %s)
                AND l.mode_execution = (SELECT id FROM ra_controls_catalog_mode_execution WHERE mode_execution = %s)
            )
 
            SELECT
                c.control_id,
                c.control_name,
                c.famille,
                c.frequence,
                c.description,
 
                COALESCE(r.nb_items, 0) AS nb_items,
                COALESCE(r.severite, 'OK') AS severite,
 
                r.montant_impacte,
                r.date_controle
 
            FROM ra_controls_catalog c
 
            LEFT JOIN ranked r
                ON r.control_id = c.control_id
            AND r.rn = 1
 
            ORDER BY c.control_id
 
        """, (
            date_controle,
            perimetre,
            mode_execution
        ))
 
    def get_detailsOld(self, control_id, date_controle):
        return fetch_all("""
            SELECT cle_metier, categorie, detail, date_controle
            FROM ra_controls_details
            WHERE control_id = %s
              AND date_controle = %s
            ORDER BY id
            LIMIT 100
        """, (control_id, date_controle))
 
    def get_details(self, control_id, date_controle, perimetre="FXL", mode_execution="COMMIT"):
        return fetch_all("""
            SELECT cle_metier, categorie, detail, date_controle
            FROM ra_controls_details
            WHERE control_id = %s
            AND date_controle = %s
            AND catalog_category_id = (
                SELECT id FROM ra_controls_catalog_category WHERE category = %s
            )
            AND mode_execution = (
                SELECT id FROM ra_controls_catalog_mode_execution WHERE mode_execution = %s
            )
            ORDER BY id
            LIMIT 100
        """, (control_id, date_controle, perimetre, mode_execution))
 
    def get_log_summary(self, control_id, date_controle):
        return fetch_all("""
            SELECT categorie, nb_items, montant_impacte, severite
            FROM ra_controls_log
            WHERE control_id = %s
              AND date_controle = %s
            ORDER BY
                CASE severite
                    WHEN 'CRITIQUE' THEN 1
                    WHEN 'ATTENTION' THEN 2
                    ELSE 3
                END,
                nb_items DESC
        """, (control_id, date_controle))
 
    def get_trendOld(self, control_id, date_controle, limit=7):
        return fetch_all("""
            SELECT date_controle, COALESCE(SUM(nb_items), 0) AS nb_items
            FROM ra_controls_log
            WHERE control_id = %s
              AND date_controle <= %s
            GROUP BY date_controle
            ORDER BY date_controle DESC
            LIMIT %s
        """, (control_id, date_controle, limit))
 
    def get_trend(self, control_id, date_controle, perimetre="FXL", mode_execution="COMMIT", limit=7):
        return fetch_all("""
            SELECT date_controle, COALESCE(SUM(nb_items), 0) AS nb_items
            FROM ra_controls_log
            WHERE control_id = %s
            AND date_controle <= %s
            AND severite != 'OK'
            AND catalog_category_id = (
                SELECT id FROM ra_controls_catalog_category WHERE category = %s
            )
            AND mode_execution = (
                SELECT id FROM ra_controls_catalog_mode_execution WHERE mode_execution = %s
            )
            GROUP BY date_controle
            ORDER BY date_controle DESC
            LIMIT %s
        """, (control_id, date_controle, perimetre, mode_execution, limit))
 
 