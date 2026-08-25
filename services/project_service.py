import os
from dataclasses import dataclass

from storage.models import Build, Deployment, Pipeline, Project


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

    def update_project(self, name, new_name=None, path=None):
        if path is not None and not os.path.isdir(path):
            raise ValueError("Project path does not exist or is not a directory")
        session = self.database.get_session()
        try:
            project = session.get(Project, name)
            if project is None:
                raise ValueError(f"Project '{name}' does not exist")
            if new_name and new_name != name and session.get(Project, new_name):
                raise ValueError(f"Project '{new_name}' already exists")
            if path is not None:
                project.path = path
            if new_name and new_name != name:
                for pipeline in session.query(Pipeline).filter_by(project_name=name):
                    pipeline.project_name = new_name
                for build in session.query(Build).filter_by(project_name=name):
                    build.project_name = new_name
                for deployment in session.query(Deployment).filter_by(project_name=name):
                    deployment.project_name = new_name
                project.name = new_name
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_project(self, name):
        session = self.database.get_session()
        try:
            project = session.get(Project, name)
            if project is None:
                raise ValueError(f"Project '{name}' does not exist")
            session.delete(project)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


    