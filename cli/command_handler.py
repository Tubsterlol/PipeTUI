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
from services.project_service import ProjectService
from core.config import Config
from cli.alert_commands import alerts


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option("0.1.0", prog_name="PipeTUI")
@click.pass_context
def cli(ctx):
    """PipeTUI DevOps CLI"""

    if ctx.invoked_subcommand is None:
        from tui.app import PipeTUIApp

        PipeTUIApp().run()


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


@build.command(name="list")
@click.argument("project", required=False)
def history(project):
    """Show build history"""
    builds = (
        BuildService(Database()).get_project_builds(project)
        if project
        else BuildService(Database()).get_builds()
    )

    if not builds:
        click.echo("No builds found.")
        return

    click.echo("\nBUILD HISTORY")
    click.echo("-------------")

    click.echo("BUILD    PIPELINE       STATUS      DURATION")
    for item in builds:
        click.echo(
            f"#{item.id:<7} {item.pipeline_name or 'manual':<14} "
            f"{item.status:<11} {item.duration if item.duration is not None else '-'}s"
        )

    click.echo("")


build.add_command(history, name="history")


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


@build.command(name="logs")
@click.argument("build_id", type=int)
def build_logs(build_id):
    """Show output for a build."""
    db = Database()
    build = db.get_build_log(build_id)
    if build is None:
        click.echo(f"Build {build_id} not found.")
        return
    click.echo(f"BUILD #{build[0]}")
    click.echo(f"Project: {build[1]}")
    click.echo(f"Status: {build[2]}")
    click.echo(f"Duration: {build[7] if build[7] is not None else '-'}s")
    click.echo("\nLOG\n---")
    click.echo(build[3] or "No log available.")


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


@project.command()
@click.argument("name")
@click.option("--name", "new_name")
@click.option("--path")
def edit(name, new_name, path):
    """Update project name and/or filesystem path."""
    if new_name is None and path is None:
        raise click.UsageError("Provide --name or --path.")
    ProjectService(Database()).update_project(name, new_name=new_name, path=path)
    click.echo(f"Project '{name}' updated.")


@project.command()
@click.argument("name")
def delete(name):
    """Delete a project and its related data."""
    ProjectService(Database()).delete_project(name)
    click.echo(f"Project '{name}' deleted.")


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
def create(project, name):
    """Create an empty pipeline for a registered project."""
    db = Database()
    if db.get_project(project) is None:
        raise click.ClickException(
            f"Project '{project}' does not exist. "
            "Use: pipetui pipeline create PROJECT [PIPELINE_NAME]"
        )
    db.create_pipeline(project, name)

    click.echo(f"Pipeline '{name}' created for {project}")


@pipeline.command(name="list")
@click.argument("project")
def list_pipelines(project):
    """List pipelines for a project."""
    pipelines = Database().get_project_pipelines(project)
    if not pipelines:
        click.echo("No pipelines found.")
        return
    for item in pipelines:
        click.echo(f"{item['id']}  {item['name']}")


@pipeline.command(name="edit")
@click.argument("project")
@click.argument("pipeline_name")
@click.option("--name", "new_name", required=True)
def edit_pipeline(project, pipeline_name, new_name):
    """Rename a pipeline."""
    db = Database()
    pipeline = db.get_pipeline_by_name(pipeline_name, project)
    if pipeline is None:
        click.echo(f"Pipeline '{pipeline_name}' not found for {project}.")
        return
    PipelineService(db).update_pipeline(pipeline["id"], new_name)
    click.echo(f"Pipeline '{pipeline_name}' renamed to '{new_name}'.")


@pipeline.command(name="delete")
@click.argument("project")
@click.argument("pipeline_name")
def delete_pipeline(project, pipeline_name):
    """Delete a pipeline."""
    db = Database()
    pipeline = db.get_pipeline_by_name(pipeline_name, project)
    if pipeline is None:
        click.echo(f"Pipeline '{pipeline_name}' not found for {project}.")
        return
    PipelineService(db).delete_pipeline(pipeline["id"])
    click.echo(f"Pipeline '{pipeline_name}' deleted.")


@cli.group()
def step():
    """Pipeline step commands."""
    pass


@step.command(name="list")
@click.argument("project")
@click.argument("pipeline_name")
def list_steps(project, pipeline_name):
    """List steps for a pipeline."""
    db = Database()
    pipeline_ref = db.get_pipeline_by_name(pipeline_name, project)
    pipeline = PipelineService(db).get_pipeline(pipeline_ref["id"]) if pipeline_ref else None
    if pipeline is None:
        click.echo(f"Pipeline '{pipeline_name}' not found for {project}.")
        return
    click.echo(f"PIPELINE: {pipeline_name}")
    for item in pipeline["steps"]:
        click.echo(f"{item['order']}  {item['value']}")


@step.command(name="add")
@click.argument("project")
@click.argument("pipeline_name")
@click.argument("step_order", type=int)
@click.argument("command")
def add_step(project, pipeline_name, step_order, command):
    """Append a command step to a pipeline."""
    db = Database()
    service = PipelineService(db)
    pipeline_ref = db.get_pipeline_by_name(pipeline_name, project)
    pipeline = service.get_pipeline(pipeline_ref["id"]) if pipeline_ref else None
    if pipeline is None:
        click.echo(f"Pipeline '{pipeline_name}' not found for {project}.")
        return
    if step_order != len(pipeline["steps"]) + 1:
        raise click.UsageError("Step order must append at the end of the pipeline.")
    service.add_step(pipeline_ref["id"], step_order, "command", command)
    click.echo(f"Step added to pipeline '{pipeline_name}'.")


@step.command(name="edit")
@click.argument("project")
@click.argument("pipeline_name")
@click.argument("step_order", type=int)
@click.argument("command")
def edit_step(project, pipeline_name, step_order, command):
    """Edit a pipeline step command."""
    db = Database()
    pipeline_ref = db.get_pipeline_by_name(pipeline_name, project)
    pipeline = PipelineService(db).get_pipeline(pipeline_ref["id"]) if pipeline_ref else None
    if pipeline is None or not 1 <= step_order <= len(pipeline["steps"]):
        raise click.UsageError("Pipeline or step order not found.")
    PipelineService(db).update_step(pipeline["steps"][step_order - 1]["id"], command)
    click.echo(f"Step {step_order} updated in pipeline '{pipeline_name}'.")


@step.command(name="delete")
@click.argument("project")
@click.argument("pipeline_name")
@click.argument("step_order", type=int)
def delete_step(project, pipeline_name, step_order):
    """Delete a pipeline step."""
    db = Database()
    pipeline_ref = db.get_pipeline_by_name(pipeline_name, project)
    pipeline = PipelineService(db).get_pipeline(pipeline_ref["id"]) if pipeline_ref else None
    if pipeline is None or not 1 <= step_order <= len(pipeline["steps"]):
        raise click.UsageError("Pipeline or step order not found.")
    PipelineService(db).delete_step(pipeline["steps"][step_order - 1]["id"])
    click.echo(f"Step {step_order} deleted from pipeline '{pipeline_name}'.")


@pipeline.command()
@click.argument("pipeline_ref")
@click.argument("pipeline_name", required=False)
@click.option(
    "--name",
    "pipeline_name_option",
    default=None,
    help="Pipeline name when passing a project.",
)
def run(pipeline_ref, pipeline_name, pipeline_name_option):
    """Run pipeline"""
    db = Database()
    project_data = db.get_project(pipeline_ref)
    if project_data is not None:
        project = pipeline_ref
        pipeline = db.get_pipeline_by_name(
            pipeline_name or pipeline_name_option or "default", project
        )
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


cli.add_command(alerts)
