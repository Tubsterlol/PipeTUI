from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from core.event_bus import EventBus
from services.alert_service import AlertService
from services.build_service import BuildService
from services.deploy_service import DeployService
from services.pipeline_service import PipelineService
from services.project_service import ProjectService
from storage.database import Database


class PipeTUIApp:
    """Rich-only interactive dashboard for PipeTUI."""

    def __init__(self, database=None, console=None):
        self.database = database or Database()
        self.console = console or Console()
        event_bus = EventBus()
        self.project_service = ProjectService(self.database)
        self.pipeline_service = PipelineService(self.database, event_bus)
        self.build_service = BuildService(self.database, event_bus)
        self.deploy_service = DeployService(event_bus, self.database)
        self.alert_service = AlertService(event_bus, self.database)
        self.projects = []
        self.pipelines = []
        self.builds = []
        self.project_index = 0
        self.pipeline_index = 0
        self.build_index = 0
        self.notice = "Ready"

    def run(self) -> None:
        try:
            self.refresh()
            while True:
                self.console.clear()
                self.console.print(self.render())
                command = self.console.input("\n[bold yellow]pipetui>[/] ").strip().lower()
                if not self.handle_command(command):
                    break
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            self.database.close()

    def refresh(self) -> None:
        self.projects = self.project_service.list_projects()
        self.project_index = min(self.project_index, max(len(self.projects) - 1, 0))
        if self.projects:
            self.load_project(self.projects[self.project_index])
        else:
            self.pipelines = []
            self.builds = []
            self.notice = "No projects registered"

    def load_project(self, project) -> None:
        self.pipelines = self.pipeline_service.get_project_pipelines(project.name)
        self.builds = self.build_service.get_project_builds(project.name)
        self.pipeline_index = min(self.pipeline_index, max(len(self.pipelines) - 1, 0))
        self.build_index = min(self.build_index, max(len(self.builds) - 1, 0))

    def handle_command(self, command: str) -> bool:
        if command in {"q", "quit", "exit"}:
            return False
        if command in {"r", "refresh"}:
            self.refresh()
            self.notice = "Refreshed"
        elif command in {"h", "help", "?"}:
            self.show_help()
        elif command.startswith("p "):
            self.select_project(command[2:])
        elif command.startswith("l "):
            self.select_pipeline(command[2:])
        elif command.startswith("b "):
            self.select_build(command[2:])
        elif command == "c" or command.startswith("c "):
            self.create_pipeline(command[2:].strip())
        elif command == "run":
            self.run_pipeline()
        elif command == "build":
            self.run_build()
        elif command == "deploy":
            self.deploy()
        elif command == "logs":
            self.show_logs()
        else:
            self.notice = f"Unknown command: {command}. Press h for help."
        return True

    def select_project(self, value: str) -> None:
        try:
            index = int(value) - 1
            if not 0 <= index < len(self.projects):
                raise ValueError
        except ValueError:
            self.notice = "Project number not found"
            return
        self.project_index = index
        self.load_project(self.projects[index])
        self.notice = f"Selected project: {self.projects[index].name}"

    def select_pipeline(self, value: str) -> None:
        try:
            index = int(value) - 1
            if not 0 <= index < len(self.pipelines):
                raise ValueError
        except ValueError:
            self.notice = "Pipeline number not found"
            return
        self.pipeline_index = index
        self.notice = f"Selected pipeline: {self.pipelines[index]['name']}"

    def select_build(self, value: str) -> None:
        try:
            index = int(value) - 1
            if not 0 <= index < len(self.builds):
                raise ValueError
        except ValueError:
            self.notice = "Build number not found"
            return
        self.build_index = index
        self.notice = f"Selected build: #{self.builds[index].id}"

    def create_pipeline(self, name: str = "") -> None:
        project = self.current_project
        if project is None:
            self.notice = "Select a project first"
            return
        if not name:
            name = self.console.input("Pipeline name: ").strip()
        if not name:
            self.notice = "Pipeline creation cancelled"
            return
        try:
            pipeline_id = self.pipeline_service.create_pipeline(project.name, name)
            default_steps = ("pytest", "ruff check .", "ruff format --check .")
            for order, command in enumerate(default_steps, start=1):
                self.pipeline_service.add_step(pipeline_id, order, "command", command)
            self.refresh()
            self.pipeline_index = next(
                (
                    index
                    for index, pipeline in enumerate(self.pipelines)
                    if pipeline["id"] == pipeline_id
                ),
                self.pipeline_index,
            )
            self.notice = f"Created pipeline: {name}"
        except Exception as error:
            self.notice = f"Pipeline creation failed: {error}"

    def run_pipeline(self) -> None:
        if not self.pipelines:
            self.notice = "No pipeline available"
            return
        pipeline = self.pipelines[self.pipeline_index]
        try:
            result = self.pipeline_service.run_pipeline(pipeline["id"])
            self.notice = f"Pipeline {result['status']}: build #{result['build_id']}"
            self.refresh()
        except Exception as error:
            self.notice = f"Pipeline failed: {error}"

    def run_build(self) -> None:
        project = self.current_project
        if project is None:
            self.notice = "No project selected"
            return
        try:
            result = self.build_service.run_build(
                project.name, project.path, ["echo", "Build requested"]
            )
            self.notice = f"Build {result['status']}"
            self.refresh()
        except Exception as error:
            self.notice = f"Build failed: {error}"

    def deploy(self) -> None:
        project = self.current_project
        if project is None:
            self.notice = "No project selected"
            return
        try:
            self.deploy_service.deploy(project.name, "default")
            self.notice = f"Deployed {project.name}"
        except Exception as error:
            self.notice = f"Deploy failed: {error}"

    def show_logs(self) -> None:
        build = self.current_build
        if build is None:
            self.notice = "Select a build first"
            return
        log = self.build_service.get_build_log(build.id)
        output = log[3] if log else "No log available."
        self.console.clear()
        self.console.print(Panel(output or "No output.", title=f"BUILD #{build.id} LOG"))
        self.console.input("\nPress Enter to return...")

    def show_help(self) -> None:
        commands = Table(box=box.SIMPLE, expand=True, padding=(0, 2))
        commands.add_column("KEY / COMMAND", style="bold yellow", width=20)
        commands.add_column("ACTION", style="bold white", width=18)
        commands.add_column("HOW TO USE", style="grey70")
        commands.add_row("p N", "Select project", "Choose project number N")
        commands.add_row("l N", "Select pipeline", "Choose pipeline number N")
        commands.add_row("b N", "Select build", "Choose build number N")
        commands.add_row("c [NAME]", "Create pipeline", "Create a pipeline for the selected project")
        commands.add_row("run", "Run pipeline", "Select a pipeline first")
        commands.add_row("build", "Run build", "Build the selected project")
        commands.add_row("deploy", "Deploy", "Deploy selected project to default")
        commands.add_row("logs", "View logs", "Select a build first")
        commands.add_row("r / refresh", "Reload", "Reload projects and history")
        commands.add_row("h / ?", "This help", "Open this command reference")
        commands.add_row("q / quit", "Exit", "Close the dashboard")

        workflow = Text.from_markup(
            "[bold yellow]Typical workflow[/bold yellow]\n"
            "p 1  ->  l 1  ->  run\n"
            "Select by the number shown in the dashboard, then run an action.\n"
            "Press [bold]Enter[/bold] after every command.",
        )
        self.console.clear()
        self.console.print(
            Group(
                Panel(commands, title="COMMAND REFERENCE", border_style="yellow"),
                Panel(workflow, title="HOW IT WORKS", border_style="grey35"),
            )
        )
        self.console.input("\nPress Enter to return...")

    @property
    def current_project(self):
        return self.projects[self.project_index] if self.projects else None

    @property
    def current_pipeline(self):
        return self.pipelines[self.pipeline_index] if self.pipelines else None

    @property
    def current_build(self):
        return self.builds[self.build_index] if self.builds else None

    def render(self):
        project = self.current_project
        title = Text("PIPE TUI", style="bold bright_cyan")
        title.append("  /  ", style="grey50")
        title.append("LOCAL DELIVERY CONTROL", style="bold white")
        header = Panel(
            Group(
                title,
                Text(
                    f"{project.name if project else 'No project selected'}  "
                    f"|  {self.notice}",
                    style="grey70",
                ),
            ),
            border_style="bright_cyan",
            box=box.DOUBLE,
            padding=(0, 1),
        )

        metrics = Table.grid(expand=True, padding=(0, 2))
        metrics.add_column(justify="center")
        metrics.add_column(justify="center")
        metrics.add_column(justify="center")
        metrics.add_column(justify="center")
        metrics.add_row(
            Text(f"{len(self.projects)}", style="bold bright_cyan"),
            Text(f"{len(self.pipelines)}", style="bold bright_cyan"),
            Text(f"{len(self.builds)}", style="bold bright_cyan"),
            Text(
                self.current_pipeline["name"] if self.current_pipeline else "-",
                style="bold bright_cyan",
            ),
        )
        metrics.add_row(
            Text("PROJECTS (p)", style="grey58"),
            Text("PIPELINES", style="grey58"),
            Text("BUILDS", style="grey58"),
            Text("ACTIVE PIPELINE", style="grey58"),
        )

        projects = Table(box=None, expand=True, padding=(0, 1))
        projects.add_column("#", style="bright_cyan", width=3)
        projects.add_column("PROJECT", style="bold white")
        for index, item in enumerate(self.projects, 1):
            style = "bold black on bright_cyan" if index - 1 == self.project_index else "white"
            projects.add_row(str(index), Text(item.name, style=style))
        if not self.projects:
            projects.add_row("-", "No projects registered")

        pipelines = Table(box=None, expand=True, padding=(0, 1))
        pipelines.add_column("#", style="bright_cyan", width=3)
        pipelines.add_column("PIPELINE", style="bold white")
        for index, item in enumerate(self.pipelines, 1):
            style = "bold black on bright_cyan" if index - 1 == self.pipeline_index else "white"
            pipelines.add_row(str(index), Text(item["name"], style=style))
        if not self.pipelines:
            pipelines.add_row("-", "No pipelines")

        builds = Table(box=box.SIMPLE_HEAVY, expand=True, padding=(0, 1))
        builds.add_column("#", style="grey58", width=8)
        builds.add_column("STATUS", width=10)
        builds.add_column("PIPELINE", style="bright_cyan")
        builds.add_column("DURATION", justify="right")
        builds.add_column("STARTED", style="grey58")
        for index, item in enumerate(self.builds[:10], 1):
            status_style = {
                "success": "bold green",
                "failed": "bold red",
                "running": "bold yellow",
            }.get(item.status, "white")
            selected = " reverse" if index - 1 == self.build_index else ""
            builds.add_row(
                f"{index} / #{item.id}",
                Text(item.status.upper(), style=status_style + selected),
                item.pipeline_name or "manual",
                f"{item.duration:.2f}s" if item.duration is not None else "-",
                self.format_time(item.started_at),
            )
        if not self.builds:
            builds.add_row("-", "No builds", "-", "-", "-")

        overview = Table.grid(padding=(0, 1))
        overview.add_column(style="grey58")
        overview.add_column(style="white")
        if project:
            overview.add_row("PROJECT", project.name)
            overview.add_row("PATH", project.path)
            overview.add_row("ACTIVE", self.current_pipeline["name"] if self.current_pipeline else "-")
            overview.add_row("LATEST", f"#{self.builds[0].id}" if self.builds else "-")
        else:
            overview.add_row("STATUS", "Waiting for a project")

        navigation = Table.grid(expand=True, padding=(0, 1))
        navigation.add_column(ratio=1)
        navigation.add_column(ratio=1)
        navigation.add_row(
            Panel(projects, title="PROJECTS  [p N]", border_style="grey35"),
            Panel(pipelines, title="PIPELINES  [l N]", border_style="grey35"),
        )
        body = Group(
            navigation,
            Panel(
                overview,
                title="SELECTED PROJECT",
                border_style="bright_cyan",
                padding=(0, 1),
            ),
            Panel(
                builds,
                title="RECENT BUILDS  [b N]",
                border_style="grey35",
                padding=(0, 1),
            ),
        )
        footer = Text(
            " p N project   l N pipeline   b N build   c create   run execute   "
            "build compile   deploy release   logs inspect   r refresh   q quit",
            style="grey70",
        )
        return Group(
            header,
            Panel(metrics, border_style="grey35", padding=(0, 1)),
            body,
            Panel(footer, border_style="grey35", padding=(0, 1)),
        )

    @staticmethod
    def format_time(value) -> str:
        return value.strftime("%Y-%m-%d %H:%M") if value is not None else "-"


if __name__ == "__main__":
    PipeTUIApp().run()
