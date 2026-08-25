import click
import json
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
from services.pipeline_service import PipelineService
from core.config import Config


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option("0.1.0", prog_name="PipeTUI")
@click.pass_context
def cli(ctx):
    """PipeTUI DevOps CLI"""

    if ctx.invoked_subcommand is None:
        from tui.screens.main import start_tui

        start_tui()


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
    build_service = BuildService(db, event_bus)

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
        click.echo(f"#{b[4]} | {b[0]} | {b[1]} | {b[2]} | {b[3]}")

    click.echo("")


build.add_command(history, name="list")


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


@logs.command(name="build")
@click.argument("build_id", type=int)
def show_build_log(build_id):
    """Show structured output for a build."""
    db = Database()
    build = db.get_build_log(build_id)

    if build is None:
        click.echo(f"Build {build_id} not found.")
        return

    click.echo(f"Build #{build[0]}")
    click.echo(f"Project: {build[1]}")
    click.echo(f"Status: {build[2]}")
    click.echo("─" * 40)

    try:
        payload = json.loads(build[3])
    except (TypeError, json.JSONDecodeError):
        payload = {"steps": [{"command": "build", "stdout": build[3], "stderr": ""}]}

    for step in payload.get("steps", []):
        click.echo(f"[{step.get('order', '?')}] {step.get('command', '')}")
        click.echo(f"$ {step.get('command', '')}")
        if step.get("stdout"):
            click.echo(step["stdout"].rstrip())
        if step.get("stderr"):
            click.echo(step["stderr"].rstrip(), err=True)
        click.echo(f"Exit code: {step.get('exit_code', 'n/a')}")
        click.echo(f"Duration: {step.get('duration', 'n/a')}s")
        click.echo("─" * 40)

    click.echo(f"BUILD {build[2].upper()}")


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

    if not os.path.isdir(path):
        click.echo("Project path does not exist or is not a directory.")
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
@click.argument("name", required=False, default="default")
@click.option(
    "--step",
    "steps",
    multiple=True,
    default=("pytest", "ruff check .", "ruff format --check ."),
    help="Command to run in order; may be supplied more than once.",
)
def create(project, name, steps):
    """Create pipeline"""
    db = Database()

    pipeline_id = db.create_pipeline(project, name)
    for order, command in enumerate(steps, start=1):
        db.add_pipeline_step(pipeline_id, order, "command", command)

    click.echo(f"Pipeline '{name}' created for {project}")


@pipeline.command()
@click.argument("pipeline_ref")
@click.option(
    "--name",
    "pipeline_name",
    default=None,
    help="Pipeline name when passing a project.",
)
def run(pipeline_ref, pipeline_name):
    """Run pipeline"""
    db = Database()
    project_data = db.get_project(pipeline_ref)
    if project_data is not None:
        project = pipeline_ref
        pipeline = db.get_pipeline_by_name(pipeline_name or "default", project)
        if pipeline is None:
            click.echo("Pipeline not found.")
            return
    else:
        pipeline = db.get_pipeline_by_name(pipeline_ref)
        if pipeline is None:
            click.echo("Project or pipeline not found.")
            return
        project = pipeline["project"]

    steps = db.get_pipeline_steps_for(project, pipeline["name"])

    if not steps:
        click.echo("No pipeline found.")
        return

    click.echo(f"\nPipeline: {pipeline['name']}")
    click.echo("")

    result = PipelineService(db).run_pipeline(pipeline["id"])

    for step in result["steps"]:
        mark = "✓" if step["status"] == "success" else "✗"
        click.echo(f"[{step['order']}/{len(steps)}] {step['command']}")
        click.echo(f"      {mark} {step['status']}")

    click.echo(f"\nPipeline {result['status']}")
    click.echo(f"Build #{result['build_id']}")
    if result["status"] == "failed":
        raise click.exceptions.Exit(1)


# -------------------------
# RESET
# -------------------------


@cli.command()
def reset():
    """Clear all history"""
    db = Database()

    db.reset_history()

    click.echo("All build, deployment, and alert history cleared.")


@cli.command()
def tui():
    """Launch the PipeTUI interface."""
    from tui.app import PipeTUIApp

    PipeTUIApp().run()
