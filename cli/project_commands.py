import click
from storage.database import Database
from services.project_service import ProjectService


@click.group()
def project():
    pass


@project.command()
@click.argument("name")
@click.argument("path")
def add(name, path):

    db = Database()
    service = ProjectService(db)

    service.add_project(name, path)


@project.command()
def list():

    db = Database()
    service = ProjectService(db)

    service.list_projects()