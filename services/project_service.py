import os
from dataclasses import dataclass

from storage.models import Project


@dataclass(frozen=True)
class ProjectRecord:
    name: str
    path: str


class ProjectService:
    def __init__(self, database):
        self.database = database

    def add_project(self, name, path):
        if not os.path.isdir(path):
            raise ValueError("Project path does not exist or is not a directory")

        session = self.database.get_session()

        try:
            project = Project(name=name, path=path)

            session.add(project)
            session.commit()
            return ProjectRecord(name=project.name, path=project.path)

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()
    def list_projects(self):
        session = self.database.get_session()

        try:
            return [
                ProjectRecord(name=project.name, path=project.path)
                for project in session.query(Project).order_by(Project.name).all()
            ]

        finally:
            session.close()

    def get_project_path(self, name):
        session = self.database.get_session()

        try:
            project = session.get(Project, name)

            return project.path if project else None

        finally:
            session.close()

    def get_project(self, name):
        session = self.database.get_session()
        try:
            project = session.get(Project, name)
            if project is None:
                return None
            return ProjectRecord(name=project.name, path=project.path)
        finally:
            session.close()


    