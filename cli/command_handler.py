import click
import threading
import os
import time

from core.event_bus import EventBus
from services.monitor_service import MonitorService
from services.alert_service import AlertService
from services.build_service import BuildService
from storage.database import Database
from services.deploy_service import DeployService
from services.log_service import LogService
from core.config import Config


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

    t = threading.Thread(target=monitor.start_monitoring, daemon=True)
    t.start()

    click.echo("\nDevOps monitoring started")
    click.echo("Press CTRL+C to stop\n")

    t.join()


@cli.command()
def status():
    """Check system status"""
    click.echo("\nPIPE TUI STATUS")
    click.echo("----------------")
    click.echo("DevOps system running\n")


# -------------------------
# BUILD COMMANDS
# -------------------------

@cli.group()
def build():
    """Build related commands"""
    pass


@build.command(name="run")
@click.argument("project")
def run_build(project):
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

    click.echo("\nBUILD RESULT")
    click.echo("-------------")
    click.echo(f"Project  : {project}")
    click.echo(f"Status   : {result['status']}")
    click.echo(f"Duration : {result['duration']}s\n")

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

    click.echo("\nBUILD HISTORY")
    click.echo("-------------")

    for b in builds:
        click.echo(f"{b[0]} | {b[1]} | {b[2]} | {b[3]}")

    click.echo("")


@build.command(name="show-logs")
@click.argument("project")
@click.option("--last", is_flag=True, help="Show last build log")
@click.option("--id", "build_id", help="Show log for specific build ID")
def show_build_logs(project, last, build_id):
    """Show build logs"""
    db = Database()

    if last:
        build = db.get_last_build(project)
        if not build:
            click.echo("No builds found.")
            return

        click.echo(f"\nBUILD LOG (ID: {build[0]})")
        click.echo("--------------------------")
        click.echo(build[5] + "\n")
        return

    if build_id:
        build = db.get_build_log(build_id)
        if not build:
            click.echo("Build not found.")
            return

        click.echo(f"\nBUILD LOG (ID: {build[0]})")
        click.echo("--------------------------")
        click.echo(build[3] + "\n")
        return

    builds = db.get_project_builds(project)

    if not builds:
        click.echo("No builds found.")
        return

    click.echo("\nPROJECT BUILDS")
    click.echo("--------------------------")

    for b in builds:
        click.echo(f"ID:{b[0]} | Status:{b[2]} | Started:{b[3]}")

    click.echo("")


@build.command()
@click.argument("project")
def tail(project):
    """Live stream build logs"""
    db = Database()

    click.echo(f"\nStreaming build logs for {project}")
    click.echo("Press CTRL+C to stop\n")

    last_length = 0

    try:
        while True:
            build = db.get_last_build_log(project)

            if not build:
                time.sleep(1)
                continue

            log = build[1] or ""

            if len(log) > last_length:
                click.echo(log[last_length:], nl=False)
                last_length = len(log)

            time.sleep(1)

    except KeyboardInterrupt:
        click.echo("\nLog streaming stopped")


# -------------------------
# DEPLOY COMMANDS
# -------------------------

@cli.group()
def deploy():
    """Deployment commands"""
    pass


@deploy.command(name="run")
@click.argument("project")
@click.argument("environment")
def run_deploy(project, environment):
    """Deploy project"""
    event_bus = EventBus()
    db = Database()

    AlertService(event_bus)
    deploy_service = DeployService(event_bus, db)

    click.echo(f"\nDeploying {project} to {environment}\n")
    deploy_service.deploy(project, environment)


@deploy.command()
def history():
    """Show deployment history"""
    db = Database()
    deployments = db.get_deployments()

    if not deployments:
        click.echo("No deployments found.")
        return

    click.echo("\nDEPLOYMENT HISTORY")
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


@logs.command(name="show")
def show_logs():
    """Show all logs"""
    LogService().show_logs()


@logs.command(name="filter")
@click.argument("level")
def filter_logs(level):
    """Filter logs by level"""
    LogService().filter_logs(level)


# -------------------------
# PROJECT COMMANDS
# -------------------------

@cli.group()
def project():
    """Project management"""
    pass


@project.command(name="list")
def list_projects():
    """List projects"""
    db = Database()
    projects = db.get_projects()

    if not projects:
        click.echo("No projects registered.")
        return

    click.echo("\nREGISTERED PROJECTS")
    click.echo("-------------------")

    for p in projects:
        click.echo(f"{p[0]} -> {p[1]}")

    click.echo("")


@project.command()
@click.argument("name")
@click.argument("path")
def add(name, path):
    """Add new project"""
    db = Database()

    if not os.path.exists(path):
        click.echo("Path does not exist.")
        return

    db.add_project(name, path)
    click.echo(f"Project '{name}' added.")


# -------------------------
# PIPELINE COMMANDS
# -------------------------

@cli.group()
def pipeline():
    """Pipeline commands"""
    pass


@pipeline.command()
@click.argument("project")
def create(project):
    """Create pipeline"""
    db = Database()

    pipeline_id = db.create_pipeline(project, "default")
    db.add_pipeline_step(pipeline_id, 1, "build", "")
    db.add_pipeline_step(pipeline_id, 2, "deploy", "prod")

    click.echo(f"Pipeline created for {project}")


@pipeline.command()
@click.argument("project")
def run(project):
    """Run pipeline"""
    db = Database()
    steps = db.get_pipeline_steps(project)

    if not steps:
        click.echo("No pipeline found.")
        return

    click.echo("\nRunning pipeline")
    click.echo("----------------")

    for order, step_type, value in steps:
        click.echo(f"Step {order}: {step_type}")

        if step_type == "build":
            os.system(f"pipetui build run {project}")

        elif step_type == "deploy":
            os.system(f"pipetui deploy run {project} {value}")


# -------------------------
# RESET
# -------------------------

@cli.command()
def reset():
    """Clear all history"""
    db = Database()

    with db.conn:
        db.conn.execute("DELETE FROM builds")
        db.conn.execute("DELETE FROM deployments")
        db.conn.execute("DELETE FROM alerts")

    click.echo("All build, deployment, and alert history cleared.")


if __name__ == "__main__":
    cli()