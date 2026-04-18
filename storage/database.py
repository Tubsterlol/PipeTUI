import sqlite3


class Database:

    def __init__(self, db_name="devops.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.initialize_tables()

    # -----------------
    # PROJECT INFO HELPERS
    # -----------------

    def get_project_builds(self, project):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, project_name, status, started_at, finished_at
            FROM builds
            WHERE project_name=?
            ORDER BY id DESC
            """,
            (project,)
        )
        return cursor.fetchall()
    
    def get_last_build(self, project):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT project_name, status, started_at, finished_at, log
            FROM builds
            WHERE project_name=?
            ORDER BY id DESC
            LIMIT 1
            """,
            (project,)
        )
        return cursor.fetchone()

    def get_last_deployment(self, project):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT environment, status
            FROM deployments
            WHERE project=?
            ORDER BY id DESC
            LIMIT 1
            """,
            (project,)
        )
        return cursor.fetchone()

    def get_build_stats(self, project):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*),
                   SUM(CASE WHEN status='success' THEN 1 ELSE 0 END)
            FROM builds
            WHERE project_name=?
            """,
            (project,)
        )
        return cursor.fetchone()
    def get_build_log(self, build_id):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT id, project_name, status, log
            FROM builds
            WHERE id = ?
            """, 
            (build_id,)
        )
        return cursor.fetchone()
    
    # -----------------
    # TABLE INITIALIZATION
    # -----------------

    def initialize_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            name TEXT PRIMARY KEY,
            path TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS builds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            status TEXT,
            started_at TEXT,
            finished_at TEXT,
            log TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS deployments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT,
            environment TEXT,
            status TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            message TEXT,
            timestamp TEXT
        )
        """)

        self.conn.commit()

    # -----------------
    # PROJECT FUNCTIONS
    # -----------------

    def add_project(self, name, path):

        try:
            self.cursor.execute(
                "INSERT INTO projects (name, path) VALUES (?, ?)",
                (name, path)
            )
            self.conn.commit()

        except sqlite3.IntegrityError:
            print(f"Project '{name}' already exists.")

    def get_projects(self):

        self.cursor.execute("SELECT name, path FROM projects")
        return self.cursor.fetchall()

    def get_project(self, name):

        self.cursor.execute(
            "SELECT name, path FROM projects WHERE name=?",
            (name,)
        )

        row = self.cursor.fetchone()

        return {"name": row[0], "path": row[1]} if row else None

    # -----------------
    # BUILD FUNCTIONS
    # -----------------

    def create_build(self, project):

        self.cursor.execute(
            """
            INSERT INTO builds (project_name, status, started_at)
            VALUES (?, ?, datetime('now'))
            """,
            (project, "running")
        )

        self.conn.commit()

        return self.cursor.lastrowid

    def finish_build(self, build_id, status, log):

        self.cursor.execute(
            """
            UPDATE builds
            SET status=?, finished_at=datetime('now'), log=?
            WHERE id=?
            """,
            (status, log, build_id)
        )

        self.conn.commit()

    def get_builds(self):

        self.cursor.execute(
            """
            SELECT id, project_name, status, started_at
            FROM builds
            ORDER BY id DESC
            """
        )

        return self.cursor.fetchall()

    # -----------------
    # DEPLOY FUNCTIONS
    # -----------------

    def insert_deployment(self, project, environment, status):

        self.cursor.execute(
            """
            INSERT INTO deployments (project, environment, status)
            VALUES (?, ?, ?)
            """,
            (project, environment, status)
        )

        self.conn.commit()

    def get_deployments(self):

        self.cursor.execute(
            "SELECT project, environment, status FROM deployments"
        )

        return self.cursor.fetchall()

    # -----------------
    # ALERT FUNCTIONS
    # -----------------

    def insert_alert(self, alert_type, message, timestamp):

        self.cursor.execute(
            """
            INSERT INTO alerts (type, message, timestamp)
            VALUES (?, ?, ?)
            """,
            (alert_type, message, timestamp)
        )

        self.conn.commit()

    def get_alerts(self):

        self.cursor.execute(
            "SELECT type, message, timestamp FROM alerts"
        )

        return self.cursor.fetchall()

    # -----------------
    # CLEANUP
    # -----------------

    def close(self):

        self.conn.close()