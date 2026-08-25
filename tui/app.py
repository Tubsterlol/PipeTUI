import json
import time

from rich import box
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from services.build_service import BuildService
from services.pipeline_service import PipelineService
from services.project_service import ProjectService
from storage.database import Database


class PipeTUIApp:
    """Read-only Rich dashboard for observing PipeTUI activity."""

    def __init__(self, database=None, console=None, refresh_interval=2):
        self.database = database or Database()
        self.console = console or Console()
        self.refresh_interval = refresh_interval
        self.project_service = ProjectService(self.database)
        self.pipeline_service = PipelineService(self.database)
        self.build_service = BuildService(self.database)
        self.projects = []
        self.pipelines = []
        self.builds = []
        self.project = None
        self.pipeline = None

    def run(self) -> None:
        try:
            with Live(self.render(), console=self.console, refresh_per_second=4) as live:
                while True:
                    self.refresh()
                    live.update(self.render())
                    time.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            pass
        finally:
            self.database.close()

    def refresh(self) -> None:
        self.projects = self.project_service.list_projects()
        self.project = self.projects[0] if self.projects else None
        if self.project is None:
            self.pipelines = []
            self.builds = []
            self.pipeline = None
            return
        self.pipelines = self.pipeline_service.get_project_pipelines(self.project.name)
        self.pipeline = self.pipelines[0] if self.pipelines else None
        self.builds = self.build_service.get_project_builds(self.project.name)

    def render(self):
        project_name = self.project.name if self.project else "No projects registered"
        pipeline_name = self.pipeline["name"] if self.pipeline else "No pipeline selected"
        header = Panel(
            Text.assemble(
                ("PIPE TUI", "bold bright_cyan"),
                (" " * max(1, 35 - len(project_name) - len(pipeline_name))),
                (f"Project: {project_name}  /  {pipeline_name}", "bold white"),
            ),
            border_style="bright_cyan",
            box=box.DOUBLE,
            padding=(0, 1),
        )

        projects = Table(box=None, expand=True, padding=(0, 1))
        projects.add_column("", width=2)
        projects.add_column("PROJECT", style="white")
        for index, item in enumerate(self.projects, start=1):
            marker = ">" if item is self.project else " "
            projects.add_row(marker, f"{index}  {item.name}")
        if not self.projects:
            projects.add_row("", "No projects registered")

        pipelines = Table(box=None, expand=True, padding=(0, 1))
        pipelines.add_column("", width=2)
        pipelines.add_column("PIPELINE", style="white")
        for index, item in enumerate(self.pipelines, start=1):
            marker = ">" if item is self.pipeline else " "
            pipelines.add_row(marker, f"{index}  {item['name']}")
        if not self.pipelines:
            pipelines.add_row("", "No pipelines")

        latest = self.builds[0] if self.builds else None
        status = latest.status.upper() if latest else "IDLE"
        status_panel = Text.assemble(
            ("STATUS\n", "grey58"),
            (status, self._status_style(status)),
            (f"\nBuild #{latest.id}" if latest else "\nNo builds yet", "grey70"),
        )
        top = Table.grid(expand=True, padding=(0, 1))
        for _ in range(3):
            top.add_column(ratio=1)
        top.add_row(
            Panel(projects, title="PROJECTS", border_style="grey35"),
            Panel(pipelines, title="PIPELINES", border_style="grey35"),
            Panel(status_panel, title="STATUS", border_style=self._status_style(status)),
        )

        project_details = Table.grid(padding=(0, 1))
        project_details.add_column(style="grey58")
        project_details.add_column(style="white")
        if self.project:
            project_details.add_row("NAME", self.project.name)
            project_details.add_row("PATH", self.project.path)
        else:
            project_details.add_row("STATUS", "Add a project with the CLI")

        steps = Table(box=None, expand=True, padding=(0, 1))
        steps.add_column("", width=4, style="bright_cyan")
        steps.add_column("COMMAND", style="white")
        steps.add_column("RESULT", justify="right")
        step_results = self._latest_step_results()
        if self.pipeline:
            for step in self.pipeline["steps"]:
                result = step_results.get(step["order"])
                if result is None:
                    result_text = "-"
                elif result["status"] == "success":
                    result_text = Text("SUCCESS", style="green")
                else:
                    result_text = Text(result["status"].upper(), style="red")
                steps.add_row(f"{step['order']}.", step["value"], result_text)
        else:
            steps.add_row("", "No pipeline selected", "")

        recent_builds = Table(box=box.SIMPLE, expand=True, padding=(0, 1))
        recent_builds.add_column("BUILD", width=8, style="grey70")
        recent_builds.add_column("PIPELINE", style="bright_cyan")
        recent_builds.add_column("STATUS", width=10)
        recent_builds.add_column("DURATION", justify="right")
        for build in self.builds[:8]:
            build_status = build.status.upper()
            recent_builds.add_row(
                f"#{build.id}",
                build.pipeline_name or "manual",
                Text(build_status, style=self._status_style(build_status)),
                f"{build.duration:.2f}s" if build.duration is not None else "-",
            )
        if not self.builds:
            recent_builds.add_row("-", "-", "No builds", "-")

        activity = self._activity()
        return Group(
            header,
            top,
            Panel(
                Group(
                    Panel(project_details, title="SELECTED PROJECT", border_style="bright_cyan"),
                    Panel(steps, title=f"ACTIVE PIPELINE  /  {pipeline_name}", border_style="yellow"),
                ),
                border_style="grey35",
                padding=(0, 1),
            ),
            Panel(recent_builds, title="RECENT BUILDS", border_style="grey35"),
            Panel(
                Text("\n".join(activity) if activity else "No recent activity", style="grey70"),
                title="RECENT ACTIVITY",
                border_style="grey35",
            ),
            Panel(
                Text("Read-only dashboard  |  Ctrl+C to exit  |  use pipetui commands to make changes", style="grey58"),
                border_style="grey35",
            ),
        )

    def _latest_step_results(self):
        if not self.builds:
            return {}
        try:
            payload = json.loads(self.builds[0].log or "{}")
        except (TypeError, json.JSONDecodeError):
            return {}
        return {step.get("order"): step for step in payload.get("steps", [])}

    def _activity(self):
        entries = []
        for build in self.builds[:4]:
            if build.status == "success":
                mark, message = "✓", f"Build #{build.id} completed"
            elif build.status == "failed":
                mark, message = "✗", f"Build #{build.id} failed"
            else:
                mark, message = "•", f"Build #{build.id} is running"
            entries.append(f"{mark}  {message}")
        return entries

    @staticmethod
    def _status_style(status):
        return {"SUCCESS": "green", "FAILED": "red", "RUNNING": "yellow"}.get(status, "grey70")


if __name__ == "__main__":
    PipeTUIApp().run()
