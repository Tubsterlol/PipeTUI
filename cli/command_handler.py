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