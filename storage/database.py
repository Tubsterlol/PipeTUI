import sqlite3

class Database:

    def __init__(self):
        self.conn = sqlite3.connect("devops.db")
        self.cursor = self.conn.cursor()
        self.initialize()

    def initialize(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS builds(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS deployments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT,
            environment TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()

    def insert_build(self, project, status):

        self.cursor.execute(
            "INSERT INTO builds(project, status) VALUES (?,?)",
            (project, status)
        )

        self.conn.commit()

    def get_builds(self):

        self.cursor.execute("SELECT * FROM builds ORDER BY id DESC")
        return self.cursor.fetchall()

    def insert_deployment(self, project, env, status):

        self.cursor.execute(
            "INSERT INTO deployments(project, environment, status) VALUES (?,?,?)",
            (project, env, status)
        )

        self.conn.commit()

    def get_deployments(self):

        self.cursor.execute("SELECT * FROM deployments ORDER BY id DESC")
        return self.cursor.fetchall()