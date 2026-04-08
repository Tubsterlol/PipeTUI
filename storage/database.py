import sqlite3


class Database:

    def __init__(self):
        self.conn = sqlite3.connect("devops.db")
        self.cursor = self.conn.cursor()
        self.initialize_tables()

    def initialize_tables(self):

        # projects registry
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            name TEXT PRIMARY KEY,
            path TEXT
        )
        """)

        # build history
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS builds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT,
            status TEXT
        )
        """)

        # deployment history
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

    def insert_project(self, name, path):

        self.cursor.execute(
            "INSERT INTO projects (name, path) VALUES (?, ?)",
            (name, path)
        )

        self.conn.commit()

    def get_projects(self):

        self.cursor.execute("SELECT name, path FROM projects")
        return self.cursor.fetchall()

    def get_project(self, name):

        self.cursor.execute(
            "SELECT name, path FROM projects WHERE name=?",
            (name,)
        )

        return self.cursor.fetchone()

    # -----------------
    # BUILD FUNCTIONS
    # -----------------

    def insert_build(self, project, status):

        self.cursor.execute(
            "INSERT INTO builds (project, status) VALUES (?, ?)",
            (project, status)
        )

        self.conn.commit()

    def get_builds(self):

        self.cursor.execute("SELECT project, status FROM builds")
        return self.cursor.fetchall()

    # -----------------
    # DEPLOY FUNCTIONS
    # -----------------

    def insert_deployment(self, project, environment, status):

        self.cursor.execute(
            "INSERT INTO deployments (project, environment, status) VALUES (?, ?, ?)",
            (project, environment, status)
        )

        self.conn.commit()

    def get_deployments(self):

        self.cursor.execute(
            "SELECT project, environment, status FROM deployments"
        )

        return self.cursor.fetchall()
    
    def insert_alert(self, alert_type, message, timestamp):

        self.cursor.execute(
            "INSERT INTO alerts (type, message, timestamp) VALUES (?, ?, ?)",
            (alert_type, message, timestamp)
        )

        self.conn.commit()


    def get_alerts(self):

        self.cursor.execute(
            "SELECT type, message, timestamp FROM alerts"
        )

        return self.cursor.fetchall()