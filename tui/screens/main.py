from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from core.event_bus import EventBus
from services.alert_service import AlertService
from services.build_service import BuildService
from services.deploy_service import DeployService
from services.pipeline_service import PipelineService
from services.project_service import ProjectService
from storage.database import Database


class PipeTUIApp(App):
	TITLE = "PipeTUI"
	SUB_TITLE = "DevOps Pipeline Manager"
	CSS_PATH = "../styles.tcss"
	BINDINGS = [("q", "quit", "Quit")]

	def __init__(self, database=None):
		super().__init__()
		self.database = database or Database()
		event_bus = EventBus()
		self.project_service = ProjectService(self.database)
		self.pipeline_service = PipelineService(self.database, event_bus)
		self.build_service = BuildService(self.database, event_bus)
		self.alert_service = AlertService(event_bus, self.database)
		self.deploy_service = DeployService(event_bus, self.database)
		self.projects = []
		self.pipelines = []

	def compose(self) -> ComposeResult:
		yield Header()
		with Horizontal(id="main"):
			with Vertical(id="left"):
				with Vertical(id="projects-panel", classes="panel"):
					yield Static("PROJECTS", classes="panel-title")
					yield ListView(id="projects")
				with Vertical(id="builds-panel", classes="panel"):
					yield Static("BUILDS", classes="panel-title")
					yield Static("No project selected", id="builds")
			with Vertical(id="right"):
				with Vertical(id="pipelines-panel", classes="panel"):
					yield Static("PIPELINES", classes="panel-title")
					yield ListView(id="pipelines")
				with Horizontal(id="bottom-panels"):
					with Vertical(id="status-panel", classes="panel"):
						yield Static("STATUS", classes="panel-title")
						yield Static("No project selected", id="status")
					with Vertical(id="activity-panel", classes="panel"):
						yield Static("ACTIVITY", classes="panel-title")
						yield Static("No activity", id="activity")
		yield Footer()

	def on_mount(self) -> None:
		self.load_projects()

	def on_unmount(self) -> None:
		self.database.close()

	def load_projects(self) -> None:
		self.projects = self.project_service.list_projects()
		project_list = self.query_one("#projects", ListView)
		project_list.clear()

		if not self.projects:
			project_list.append(ListItem(Label("No projects registered.")))
			self.query_one("#pipelines", ListView).clear()
			self.query_one("#status", Static).update("No projects registered.")
			return

		for project in self.projects:
			project_list.append(ListItem(Label(project.name)))

		project_list.index = 0
		self.show_project(self.projects[0])

	def on_list_view_selected(self, event: ListView.Selected) -> None:
		if event.list_view.id == "projects":
			self.select_project(event.list_view)
		elif event.list_view.id == "pipelines":
			self.select_pipeline(event.list_view)

	def select_project(self, project_list: ListView) -> None:
		index = project_list.index
		if index is not None and index < len(self.projects):
			self.show_project(self.projects[index])

	def show_project(self, project) -> None:
		self.load_pipelines(project.name)
		builds = self.build_service.get_project_builds(project.name)
		build_lines = [
			f"#{build.id}  {build.status.upper()}  {build.duration or '-'}s"
			for build in builds[:5]
		]
		build_text = f"Project: {project.name}\n\n"
		build_text += "\n".join(build_lines) or "No builds loaded."
		self.query_one("#builds", Static).update(build_text)
		self.query_one("#status", Static).update(
			f"Project\n  {project.name}\n\nPath\n  {project.path}"
		)
		self.query_one("#activity", Static).update(
			f"Selected project: {project.name}"
		)

	def load_pipelines(self, project: str) -> None:
		pipeline_list = self.query_one("#pipelines", ListView)
		pipeline_list.clear()
		self.pipelines = self.pipeline_service.get_project_pipelines(project)

		if not self.pipelines:
			pipeline_list.append(ListItem(Label("No pipelines.")))
			return

		for pipeline in self.pipelines:
			pipeline_list.append(ListItem(Label(f"> {pipeline['name']}")))

	def select_pipeline(self, pipeline_list: ListView) -> None:
		index = pipeline_list.index
		if index is not None and index < len(self.pipelines):
			self.show_pipeline(self.pipelines[index])

	def show_pipeline(self, pipeline: dict) -> None:
		steps = pipeline["steps"]
		step_lines = [
			f"  {step['order']}. {step['value']}" for step in steps
		]
		steps_text = "\n".join(step_lines) or "  No steps configured."
		self.query_one("#activity", Static).update(
			f"Pipeline: {pipeline['name']}\n\nSteps\n{steps_text}"
		)
		self.query_one("#status", Static).update(
			f"Pipeline\n  {pipeline['name']}\n\n"
			f"ID\n  #{pipeline['id']}\n\nSteps\n  {len(steps)}"
		)


if __name__ == "__main__":
	PipeTUIApp().run()
