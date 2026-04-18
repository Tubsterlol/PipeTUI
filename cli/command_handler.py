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


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option("0.1.0", prog_name="PipeTUI")
def cli():
    """PipeTUI DevOps CLI"""
    pass


# -------------------------
# SYSTEM COMMANDS
# -------------------------

@cli.command()
def start():
    """Start DevOps monitoring service"""

    config = Config()
    event_bus = EventBus()

    AlertService(event_bus)

    monitor = MonitorService(event_bus, config)

    t = threading.Thread(target=monitor.start_monitoring)
    t.daemon = True
    t.start()

    click.echo("")
    click.echo("DevOps monitoring started")
    click.echo("Press CTRL+C to stop")
    click.echo("")

    t.join()


@cli.command()
def status():
    """Check system status"""
    click.echo("")
    click.echo("PIPE TUI STATUS")
    click.echo("----------------")
    click.echo("DevOps system running")
    click.echo("")


# -------------------------
# BUILD COMMANDS
# -------------------------

@cli.group()
def build():
    """Build related commands"""
    pass


@build.command()
@click.argument("project")
def run(project):
    """Run build for a project"""

    event_bus = EventBus()
    db = Database()

    AlertService(event_bus)

    build_service = BuildService(event_bus, db)

    project_data = db.get_project(project)

    if not project_data:
        click.echo(f"Project '{project}' not found")
        return

    project_name = project_data["name"]
    project_path = project_data["path"]

    if os.path.exists(f"{project_path}/package.json"):
        command = ["npm", "run", "build"]

    elif os.path.exists(f"{project_path}/Makefile"):
        command = ["make"]

    elif os.path.exists(f"{project_path}/build.py"):
        command = ["python", "build.py"]

    else:
        command = ["echo", "No build system detected"]

    result = build_service.run_build(project_name, project_path, command)

    click.echo("")
    click.echo("BUILD RESULT")
    click.echo("-------------")
    click.echo(f"Project  : {project}")
    click.echo(f"Status   : {result['status']}")
    click.echo(f"Duration : {result['duration']}s")
    click.echo("")

    if result.get("stdout"):
        click.echo(result["stdout"])

    if result.get("stderr"):
        click.echo(result["stderr"])


@build.command()
def history():
    """Show build history"""

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

    click.echo("")


# -------------------------
# DEPLOY COMMANDS
# -------------------------

@cli.group()
def deploy():
    """Deployment commands"""
    pass


@deploy.command()
@click.argument("project")
@click.argument("environment")
def run(project, environment):
    """Deploy project to environment"""

    event_bus = EventBus()
    db = Database()

    AlertService(event_bus)

    deploy_service = DeployService(event_bus, db)

    click.echo("")
    click.echo(f"Deploying {project} to {environment}")
    click.echo("")

    deploy_service.deploy(project, environment)


@deploy.command()
def history():
    """Show deployment history"""

    db = Database()

    deployments = db.get_deployments()

    if not deployments:
        click.echo("No deployments found.")
        return

    click.echo("")
    click.echo("DEPLOYMENT HISTORY")
    click.echo("------------------")

    for d in deployments:
        click.echo(d)

    click.echo("")


# -------------------------
# LOG COMMANDS
# -------------------------

@cli.group()
def logs():
    """Log related commands"""
    pass


@logs.command()
def show():
    """Show all logs"""

    logger = LogService()
    logger.show_logs()


@logs.command()
@click.argument("level")
def filter(level):
    """Filter logs by level"""

    logger = LogService()
    logger.filter_logs(level)


# -------------------------
# PROJECT COMMANDS
# -------------------------

@cli.group()
def project():
    """Project management commands"""
    pass


@project.command()
def list():
    """List registered projects"""

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
    """Register a new project"""

    db = Database()

    if not os.path.exists(path):
        click.echo("Path does not exist.")
        return

    db.add_project(name, path)

    click.echo(f"Project '{name}' added.")


# -------------------------
# RESET COMMAND
# -------------------------

@cli.command()
def reset():
    """Clear build, deployment and alert history"""

    db = Database()
    cursor = db.conn.cursor()

    cursor.execute("DELETE FROM builds")
    cursor.execute("DELETE FROM deployments")
    cursor.execute("DELETE FROM alerts")

    db.conn.commit()

    click.echo("All build, deployment, and alert history cleared.")