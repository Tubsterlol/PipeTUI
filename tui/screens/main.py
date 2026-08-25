from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    RichLog,
    Static,
)

from core.event_bus import EventBus
from services.alert_service import AlertService
from services.build_service import BuildService
from services.deploy_service import DeployService
from services.pipeline_service import PipelineService
from services.project_service import ProjectService
from storage.database import Database


class CreatePipelineScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Static("Create pipeline", id="dialog-title")
        yield Input(placeholder="Pipeline name", id="pipeline-name")
        yield Input(value="pytest", placeholder="Command", id="pipeline-command")
        yield Horizontal(
            Button("Create", variant="primary", id="create"),
            Button("Cancel", id="cancel"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
            return
        name = self.query_one("#pipeline-name", Input).value.strip()
        command = self.query_one("#pipeline-command", Input).value.strip()
        if name and command:
            self.dismiss((name, command))


class PipeTUIApp(App):
    TITLE = "PipeTUI"
    SUB_TITLE = "DevOps Pipeline Manager"
    CSS_PATH = "../styles.tcss"
    BINDINGS = [
        ("r", "run_pipeline", "Run pipeline"),
        ("b", "run_build", "Build"),
        ("d", "deploy", "Deploy"),
        ("l", "show_logs", "Logs"),
        ("c", "create", "Create"),
        ("R", "refresh", "Refresh"),
        ("ctrl+p", "command_palette", "Commands"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, database=None):
        super().__init__()
        self.database = database or Database()
        event_bus = EventBus()
        self.project_service = ProjectService(self.database)
        self.pipeline_service = PipelineService(self.database, event_bus)
        self.build_service = BuildService(self.database, event_bus)
        self.deploy_service = DeployService(event_bus, self.database)
        self.alert_service = AlertService(event_bus, self.database)
        self.projects = []
        self.pipelines = []
        self.builds = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main"):
            with Vertical(id="left"):
                with Vertical(id="projects-panel", classes="panel"):
                    yield Static("PROJECTS", classes="panel-title")
                    yield ListView(id="projects")
                with Vertical(id="pipelines-panel", classes="panel"):
                    yield Static("PIPELINES", classes="panel-title")
                    yield ListView(id="pipelines")
            with Vertical(id="right"):
                with Vertical(id="builds-panel", classes="panel"):
                    yield Static("BUILDS", classes="panel-title")
                    yield ListView(id="builds")
                with Horizontal(id="bottom-panels"):
                    with Vertical(id="details-panel", classes="panel"):
                        yield Static("DETAILS", classes="panel-title")
                        yield RichLog(id="details", wrap=True, highlight=True)
                    with Vertical(id="activity-panel", classes="panel"):
                        yield Static("ACTIVITY", classes="panel-title")
                        yield Static("No activity.", id="activity")
        yield Footer()

    def on_mount(self) -> None:
        self.load_projects()
        self.refresh_activity()
        self.set_details("Select a project or pipeline.")

    def on_unmount(self) -> None:
        self.database.close()

    def load_projects(self) -> None:
        self.projects = self.project_service.list_projects()
        project_list = self.query_one("#projects", ListView)
        project_list.clear()
        for project in self.projects:
            project_list.append(ListItem(Label(project.name), classes="data-row"))
        if self.projects:
            project_list.index = 0
            self.show_project(self.projects[0])
        else:
            project_list.append(ListItem(Label("No projects registered.")))
            self.query_one("#pipelines", ListView).clear()
            self.query_one("#pipelines", ListView).append(
                ListItem(Label("No pipelines."))
            )
            self.query_one("#builds", ListView).clear()
            self.set_details("No projects registered.")

    def show_project(self, project) -> None:
        self.load_pipelines(project.name)
        self.builds = self.build_service.get_project_builds(project.name)
        build_list = self.query_one("#builds", ListView)
        build_list.clear()
        for build in self.builds:
            mark = self.status_icon(build.status)
            duration = f"{build.duration:.2f}s" if build.duration is not None else "-"
            started = self.format_time(build.started_at)
            build_list.append(
                ListItem(
                    Label(f"#{build.id} {mark} {build.status} {duration} {started}"),
                    classes=f"data-row {build.status}",
                )
            )
        if self.builds:
            build_list.index = 0
        self.set_details(
            f"Project: {project.name}\n\nPath: {project.path}"
        )

    def load_pipelines(self, project: str) -> None:
        self.pipelines = self.pipeline_service.get_project_pipelines(project)
        pipeline_list = self.query_one("#pipelines", ListView)
        pipeline_list.clear()
        for pipeline in self.pipelines:
            pipeline_list.append(
                ListItem(Label(pipeline["name"]), classes="data-row")
            )
        if not self.pipelines:
            pipeline_list.append(ListItem(Label("No pipelines.")))
        else:
            pipeline_list.index = 0

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = event.list_view.index
        if index is None:
            return
        if event.list_view.id == "projects" and index < len(self.projects):
            self.show_project(self.projects[index])
        elif event.list_view.id == "pipelines" and index < len(self.pipelines):
            self.show_pipeline(self.pipelines[index])
        elif event.list_view.id == "builds" and index < len(self.builds):
            self.show_build(self.builds[index])

    def show_pipeline(self, pipeline: dict) -> None:
        steps = "\n".join(
            f"{step['order']}. {step['value']}" for step in pipeline["steps"]
        ) or "No steps configured."
        self.set_details(
            f"Pipeline: {pipeline['name']}\n\n{steps}"
        )

    def show_build(self, build) -> None:
        self.set_details(
            f"Build #{build.id}\n\nProject: {build.project}\n"
            f"Status: {self.status_icon(build.status)} {build.status}\n"
            f"Started: {self.format_time(build.started_at)}\n"
            f"Duration: {build.duration or '-'}s\nExit: {build.exit_code}"
        )

    def set_details(self, text: str) -> None:
        details = self.query_one("#details", RichLog)
        details.clear()
        details.write(text)

    @staticmethod
    def status_icon(status: str) -> str:
        return "[green]✓[/]" if status == "success" else "[red]✗[/]"

    @staticmethod
    def format_time(value) -> str:
        return value.strftime("%Y-%m-%d %H:%M") if value else "-"

    def selected_project(self):
        index = self.query_one("#projects", ListView).index
        return self.projects[index] if index is not None and index < len(self.projects) else None

    def selected_pipeline(self):
        index = self.query_one("#pipelines", ListView).index
        return self.pipelines[index] if index is not None and index < len(self.pipelines) else None

    def action_run_pipeline(self) -> None:
        pipeline = self.selected_pipeline()
        if pipeline is None:
            return self.notify("Select a pipeline first.")
        try:
            self.pipeline_service.run_pipeline(pipeline["id"])
            self.refresh_project()
            self.notify(f"Pipeline {pipeline['name']} finished.")
        except Exception as error:
            self.notify(f"Pipeline failed: {error}", severity="error")

    def action_run_build(self) -> None:
        project = self.selected_project()
        if project is None:
            return self.notify("Select a project first.")
        try:
            self.build_service.run_build(
                project.name, project.path, ["echo", "Build requested"]
            )
            self.refresh_project()
        except Exception as error:
            self.notify(f"Build failed: {error}", severity="error")

    def action_deploy(self) -> None:
        project = self.selected_project()
        if project is None:
            return self.notify("Select a project first.")
        try:
            self.deploy_service.deploy(project.name, "default")
            self.refresh_activity()
        except Exception as error:
            self.notify(f"Deploy failed: {error}", severity="error")

    def action_show_logs(self) -> None:
        index = self.query_one("#builds", ListView).index
        if index is None or index >= len(self.builds):
            return self.notify("Select a build first.")
        log = self.build_service.get_build_log(self.builds[index].id)
        self.set_details(log[3] if log else "No log available.")

    def action_create(self) -> None:
        project = self.selected_project()
        if project is not None:
            self.push_screen(CreatePipelineScreen(), self.create_pipeline(project.name))

    def create_pipeline(self, project):
        def callback(value):
            if value is None:
                return
            name, command = value
            try:
                pipeline_id = self.pipeline_service.create_pipeline(project, name)
                self.pipeline_service.add_step(pipeline_id, 1, "command", command)
                self.refresh_project()
            except Exception as error:
                self.notify(f"Create failed: {error}", severity="error")
        return callback

    def action_refresh(self) -> None:
        self.load_projects()
        self.refresh_activity()
        self.notify("Refreshed.")

    def refresh_project(self) -> None:
        project = self.selected_project()
        if project is not None:
            self.show_project(project)
        self.refresh_activity()

    def refresh_activity(self) -> None:
        deployments = self.deploy_service.get_deployments()[:5]
        alerts = self.alert_service.get_alerts()[:5]
        lines = [
            f"{self.status_icon(item[2])} Deploy {item[0]} / {item[1]}: {item[2]}"
            for item in deployments
        ]
        lines += [
            f"[yellow]![/] Alert {item[1]}: {item[2]} ({item[3]})"
            for item in alerts
        ]
        self.query_one("#activity", Static).update("\n".join(lines) or "No activity.")


if __name__ == "__main__":
    PipeTUIApp().run()
