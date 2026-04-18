import click
from datetime import datetime
from storage.database import Database


@click.group()
def project():
    pass


@project.command()
def list():

    db = Database()

    projects = db.get_projects()

    if not projects:
        click.echo("No projects registered.")
        return

    click.echo("")
    click.echo("REGISTERED PROJECTS")
    click.echo("-------------------")

    for p in projects:
        click.echo(f"{p[0]} -> {p[1]}")

    click.echo("")


@project.command()
@click.argument("name")
@click.argument("path")
def add(name, path):

    import os

    db = Database()

    if not os.path.exists(path):
        click.echo("Path does not exist.")
        return

    db.add_project(name, path)

    click.echo(f"Project '{name}' added.")


@project.command()
@click.argument("name")
def info(name):

    db = Database()

    project_data = db.get_project(name)

    if not project_data:
        click.echo("Project not found.")
        return

    path = project_data["path"]

    last_build = db.get_last_build(name)
    last_deploy = db.get_last_deployment(name)
    stats = db.get_build_stats(name)

    click.echo("")
    click.echo("PROJECT INFO")
    click.echo("----------------------")
    click.echo(f"Name: {name}")
    click.echo(f"Path: {path}")
    click.echo("")

    last_build = db.get_last_build(name)

    if last_build:
        status = last_build[0]
        started = last_build[1]
        finished = last_build[2]

        duration = "N/A"

        if started and finished:
            from datetime import datetime

            start_time = datetime.fromisoformat(started)
            end_time = datetime.fromisoformat(finished)

            duration = round((end_time - start_time).total_seconds(), 2)

        click.echo("")
        click.echo("Last Build")
        click.echo(f"Status: {status}")
        click.echo(f"Duration: {duration}s")

    else:
        click.echo("")
        click.echo("No builds found.")

    last_deploy = db.get_last_deployment(name)

    if last_deploy:
        environment = last_deploy[0]
        status = last_deploy[1]

        click.echo("")
        click.echo("Last Deployment")
        click.echo(f"Environment: {environment}")
        click.echo(f"Status: {status}")

    else:
        click.echo("")
        click.echo("No deployments found.")

    if stats:

        total, success = stats
        success = success or 0
        failed = total - success if total else 0
        rate = (success / total * 100) if total else 0

        click.echo("Build Statistics")
        click.echo(f"Total Builds: {total}")
        click.echo(f"Successful: {success}")
        click.echo(f"Failed: {failed}")
        click.echo(f"Success Rate: {rate:.1f}%")
        click.echo("")