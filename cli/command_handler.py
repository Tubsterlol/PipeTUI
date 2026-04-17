import click
import threading
import os

from core.event_bus import EventBus
from services.monitor_service import MonitorService
from services.alert_service import AlertService
from services.build_service import BuildService
from storage.database import Database
from services.deploy_service import DeployService
from services.log_service import LogService
from config import Config


@click.group()
def cli():
    pass


# -------------------------
# SYSTEM COMMANDS
# -------------------------

@cli.command()
def start():

    config = Config()
    event_bus = EventBus()

    AlertService(event_bus)

    monitor = MonitorService(event_bus, config)

    t = threading.Thread(target=monitor.start_monitoring)
    t.start()

    print("DevOps monitoring started")

    t.join()


@cli.command()
def status():
    print("DevOps system running")


# -------------------------
# BUILD COMMANDS
# -------------------------

@cli.group()
def build():
    pass


@build.command()
@click.argument("project")
def run(project):

    event_bus = EventBus()
    db = Database()

    AlertService(event_bus)

    build_service = BuildService(event_bus, db)

    project_data = db.get_project(project)

    if not project_data:
        click.echo(f"Project '{project}' not found")
        return

    project_path = project_data["path"]

    # Detect build system
    if os.path.exists(f"{project_path}/package.json"):
        command = ["npm", "run", "build"]

    elif os.path.exists(f"{project_path}/Makefile"):
        command = ["make"]

    elif os.path.exists(f"{project_path}/build.py"):
        command = ["python", "build.py"]

    else:
        command = ["echo", "No build system detected"]

    result = build_service.run_build(project_path, command)

    click.echo(f"Build status: {result['status']}")
    click.echo(f"Duration: {result['duration']}s")


@build.command()
def history():

    db = Database()
    builds = db.get_builds()

    if not builds:
        click.echo("No builds found.")
        return

    click.echo("")
    click.echo("BUILD HISTORY")
    click.echo("-------------")

    for b in builds:
        click.echo(f"{b[0]} | {b[1]} | {b[2]} | {b[3]}")


# -------------------------
# DEPLOY COMMANDS
# -------------------------

@cli.group()
def deploy():
    pass


@deploy.command()
@click.argument("project")
@click.argument("environment")
def run(project, environment):

    event_bus = EventBus()
    db = Database()

    AlertService(event_bus)

    deploy_service = DeployService(event_bus, db)

    deploy_service.deploy(project, environment)


@deploy.command()
def history():

    db = Database()

    deployments = db.get_deployments()

    if not deployments:
        click.echo("No deployments found.")
        return

    for d in deployments:
        click.echo(d)


# -------------------------
# LOG COMMANDS
# -------------------------

@cli.group()
def logs():
    pass


@logs.command()
def show():

    logger = LogService()
    logger.show_logs()


@logs.command()
@click.argument("level")
def filter(level):

    logger = LogService()
    logger.filter_logs(level)


# -------------------------
# PROJECT COMMANDS
# -------------------------

@cli.group()
def project():
    pass


@project.command()
def list():

    db = Database()

    projects = db.get_projects()

    if not projects:
        click.echo("No projects registered.")
        return

    for p in projects:
        click.echo(f"{p[0]} -> {p[1]}")


# -------------------------
# RESET COMMAND
# -------------------------

@cli.command()
def reset():

    db = Database()
    cursor = db.conn.cursor()

    cursor.execute("DELETE FROM builds")
    cursor.execute("DELETE FROM deployments")
    cursor.execute("DELETE FROM alerts")

    db.conn.commit()

    click.echo("All build, deployment, and alert history cleared.")


# -------------------------
# HELP COMMAND
# -------------------------

@cli.command()
def help():

    click.echo("")
    click.echo("DEVOPS DASHBOARD")
    click.echo("----------------")
    click.echo("A lightweight CLI DevOps control system.")
    click.echo("")

    click.echo("AVAILABLE COMMANDS")
    click.echo("------------------")

    click.echo("Add a project")
    click.echo("  pipetui project add <project_name> <path>")
    click.echo("")

    click.echo("Run a build")
    click.echo("  pipetui build run <project_name>")
    click.echo("")

    click.echo("Show build history")
    click.echo("  pipetui build history")
    click.echo("")

    click.echo("Deploy a project")
    click.echo("  pipetui deploy run <project_name> <environment>")
    click.echo("")

    click.echo("Show deployment history")
    click.echo("  pipetui deploy history")
    click.echo("")

    click.echo("Reset system history")
    click.echo("  pipetui reset")
    click.echo("")