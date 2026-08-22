import os

from storage.models import Project


class ProjectService:

    def __init__(self, database):
        self.database = database

    def add_project(self, name, path):

        if not os.path.isdir(path):
            raise ValueError("Project path does not exist or is not a directory")

        session = self.database.get_session()

        try:
            project = Project(
                name=name,
                path=path
            )

            session.add(project)
            session.commit()

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def list_projects(self):

        session = self.database.get_session()

        try:
            projects = session.query(Project).all()

            return projects

        finally:
            session.close()

    def get_project_path(self, name):

        session = self.database.get_session()

        try:
            project = session.get(Project, name)

            if project:
                return project.path

            return None

        finally:
            session.close()
