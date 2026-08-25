from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from storage.database import Database


class PipeTUIApp(App):
    """PipeTUI"""

    TITLE = "PipeTUI"
    SUB_TITLE = "DevOps Pipeline Manager"
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.db = Database()

        self.projects = []
        self.pipelines = []

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="main"):
            # left pane
            with Vertical(id="left"):
                with Vertical(id="projects-panel", classes="panel"):
                    yield Static(
                        "PROJECTS",
                        classes="panel-title",
                    )

                    yield ListView(id="projects")

                with Vertical(id="builds-panel", classes="panel"):
                    yield Static(
                        "BUILDS",
                        classes="panel-title",
                    )

                    yield Static(
                        "No project selected",
                        id="builds",
                    )

            # right pane
            with Vertical(id="right"):
                with Vertical(
                    id="pipelines-panel",
                    classes="panel",
                ):
                    yield Static(
                        "PIPELINES",
                        classes="panel-title",
                    )

                    yield ListView(id="pipelines")

                with Horizontal(id="bottom-panels"):
                    with Vertical(
                        id="status-panel",
                        classes="panel",
                    ):
                        yield Static(
                            "STATUS",
                            classes="panel-title",
                        )

                        yield Static(
                            "No project selected",
                            id="status",
                        )

                    with Vertical(
                        id="activity-panel",
                        classes="panel",
                    ):
                        yield Static(
                            "ACTIVITY",
                            classes="panel-title",
                        )

                        yield Static(
                            "No activity",
                            id="activity",
                        )

        yield Footer()

    #
    def on_mount(self) -> None:
        self.load_projects()

    # projects panel
    def load_projects(self) -> None:
        self.projects = self.db.get_projects()

        project_list = self.query_one("#projects", ListView)

        project_list.clear()

        if not self.projects:
            project_list.append(ListItem(Label("No projects registered.")))

            self.query_one("#pipelines", ListView).clear()

            self.query_one("#status", Static).update("No projects registered.")

            return

        for name, path in self.projects:
            project_list.append(ListItem(Label(name)))

        project_list.index = 0

        self.show_project(self.projects[0])

    def on_list_view_selected(
        self,
        event: ListView.Selected,
    ) -> None:
        if event.list_view.id == "projects":
            self.select_project(event.list_view)

        elif event.list_view.id == "pipelines":
            self.select_pipeline(event.list_view)

    def select_project(self, project_list: ListView) -> None:
        index = project_list.index

        if index is None:
            return

        if index >= len(self.projects):
            return

        project = self.projects[index]

        self.show_project(project)

    def show_project(self, project) -> None:
        name, path = project

        self.load_pipelines(name)

        self.query_one("#builds", Static).update(
            f"Project: {name}\n\nNo builds loaded."
        )

        self.query_one("#status", Static).update(f"Project\n  {name}\n\nPath\n  {path}")

        self.query_one("#activity", Static).update(f"Selected project: {name}")

    # pipelines panel
    def load_pipelines(self, project: str) -> None:
        pipeline_list = self.query_one(
            "#pipelines",
            ListView,
        )

        pipeline_list.clear()

        with self.db.get_session() as session:
            from storage.models import Pipeline

            pipelines = (
                session.query(Pipeline)
                .filter(Pipeline.project_name == project)
                .order_by(Pipeline.id.desc())
                .all()
            )

            self.pipelines = [
                {
                    "id": pipeline.id,
                    "name": pipeline.name,
                    "project": pipeline.project_name,
                    "created_at": pipeline.created_at,
                    "steps": [
                        {
                            "order": step.step_order,
                            "type": step.step_type,
                            "value": step.step_value,
                        }
                        for step in pipeline.steps
                    ],
                }
                for pipeline in pipelines
            ]

        if not self.pipelines:
            pipeline_list.append(ListItem(Label("No pipelines.")))

            return

        for pipeline in self.pipelines:
            pipeline_list.append(ListItem(Label(f"▶ {pipeline['name']}")))

    def select_pipeline(self, pipeline_list: ListView) -> None:
        index = pipeline_list.index

        if index is None:
            return

        if index >= len(self.pipelines):
            return

        pipeline = self.pipelines[index]

        self.show_pipeline(pipeline)

    def show_pipeline(self, pipeline: dict) -> None:
        steps = pipeline["steps"]

        if steps:
            step_lines = []

            for step in steps:
                step_lines.append(f"  {step['order']}. {step['value']}")

            steps_text = "\n".join(step_lines)

        else:
            steps_text = "  No steps configured."

        self.query_one("#activity", Static).update(
            f"Pipeline: {pipeline['name']}\n\nSteps\n{steps_text}"
        )

        self.query_one("#status", Static).update(
            f"Pipeline\n"
            f"  {pipeline['name']}\n\n"
            f"ID\n"
            f"  #{pipeline['id']}\n\n"
            f"Steps\n"
            f"  {len(steps)}"
        )


if __name__ == "__main__":
    PipeTUIApp().run()
