import click
import threading

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


@cli.group()
def build():
    pass

@cli.command()
def status():
    print("DevOps system running")

@build.command()
@click.argument("project")
def run(project):

    event_bus = EventBus()
    db = Database()

    AlertService(event_bus)

    build_service = BuildService(event_bus, db)

    build_service.run_build(project)


@build.command()
def history():

    db = Database()

    builds = db.get_builds()

    for b in builds:
        print(b)

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

    for d in deployments:
        print(d)

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

@click.command()
def reset():
    db = Database()
    cursor = db.conn.cursor()

    cursor.execute("DELETE FROM builds")
    cursor.execute("DELETE FROM deployments")
    cursor.execute("DELETE FROM alerts")

    db.conn.commit()

    click.echo("All build, deployment, and alert history cleared.")

@click.command()
def help():

    click.echo("")
    click.echo("DEVOPS DASHBOARD")
    click.echo("----------------")
    click.echo("A lightweight CLI DevOps control system.")
    click.echo("")
    click.echo("The system simulates a simplified CI/CD workflow.")
    click.echo("It allows you to run builds, deploy projects, track activity,")
    click.echo("and monitor everything from a terminal dashboard.")
    click.echo("")

    click.echo("TUI DASHBOARD")
    click.echo("-------------")
    click.echo("The dashboard is a live terminal interface that displays:")
    click.echo("• System CPU and memory usage")
    click.echo("• Recent alerts")
    click.echo("• Build history")
    click.echo("• Deployment history")
    click.echo("• Recent DevOps activity")
    click.echo("")

    click.echo("AVAILABLE COMMANDS")
    click.echo("------------------")

    click.echo("Add a project")
    click.echo("  python main.py project add <project_name> <path>")
    click.echo("  Registers a project so it can be built and deployed.")
    click.echo("")

    click.echo("Run a build")
    click.echo("  python main.py build run <project_name>")
    click.echo("  Executes a build process and records the result.")
    click.echo("")

    click.echo("Deploy a project")
    click.echo("  python main.py deploy run <project_name> <environment>")
    click.echo("  Deploys a project to an environment such as dev or prod.")
    click.echo("")

    click.echo("Open the DevOps dashboard")
    click.echo("  python main.py dashboard")
    click.echo("  Starts the live monitoring TUI.")
    click.echo("")

    click.echo("Reset system history")
    click.echo("  python main.py reset")
    click.echo("  Clears build history, deployment history, and alerts.")
    click.echo("")

    click.echo("Show help")
    click.echo("  python main.py help")
    click.echo("  Displays this manual.")
    click.echo("")