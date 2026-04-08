import os


class ProjectService:

    def __init__(self, database):
        self.database = database

    def add_project(self, name, path):

        if not os.path.exists(path):
            print("Project path does not exist")
            return

        self.database.insert_project(name, path)

        print(f"Project '{name}' added")

    def list_projects(self):

        projects = self.database.get_projects()

        for name, path in projects:
            print(name, "→", path)

    def get_project_path(self, name):

        project = self.database.get_project(name)

        if project:
            return project[1]

        return None