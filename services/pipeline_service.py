import json
from datetime import datetime

from services.build_service import BuildService
from services.pipeline_executor import PipelineExecutor
from storage.models import Pipeline, PipelineStep, Project


class PipelineService:
    """Manage pipeline definitions and coordinate pipeline execution."""

    def __init__(self, database, event_bus=None):
        self.database = database
        self.event_bus = event_bus

    def create_pipeline(self, project, name):
        session = self.database.get_session()
        try:
            if session.get(Project, project) is None:
                raise ValueError(f"Project '{project}' does not exist")

            pipeline = Pipeline(
                project_name=project,
                name=name,
                created_at=datetime.now(),
            )
            session.add(pipeline)
            session.commit()
            return pipeline.id
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def add_step(self, pipeline_id, step_order, step_type, step_value):
        session = self.database.get_session()
        try:
            if session.get(Pipeline, pipeline_id) is None:
                raise ValueError(f"Pipeline {pipeline_id} does not exist")

            step = PipelineStep(
                pipeline_id=pipeline_id,
                step_order=step_order,
                step_type=step_type,
                step_value=step_value,
            )
            session.add(step)
            session.commit()
            return {
                "id": step.id,
                "order": step.step_order,
                "type": step.step_type,
                "value": step.step_value,
            }
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_pipeline(self, pipeline_id):
        session = self.database.get_session()
        try:
            pipeline = session.get(Pipeline, pipeline_id)
            if pipeline is None:
                return None
            return {
                "id": pipeline.id,
                "name": pipeline.name,
                "project": pipeline.project_name,
                "created_at": pipeline.created_at,
                "steps": [
                    {
                        "id": step.id,
                        "order": step.step_order,
                        "type": step.step_type,
                        "value": step.step_value,
                    }
                    for step in pipeline.steps
                ],
            }
        finally:
            session.close()

    def get_project_pipelines(self, project):
        return self.database.get_project_pipelines(project)

    def run_pipeline(self, pipeline_id):
        pipeline = self.get_pipeline(pipeline_id)
        if pipeline is None:
            raise ValueError(f"Pipeline {pipeline_id} does not exist")

        project = self._get_project(pipeline["project"])
        if project is None:
            raise ValueError(f"Project '{pipeline['project']}' does not exist")

        steps = [
            (step["order"], step["type"], step["value"]) for step in pipeline["steps"]
        ]
        build_service = BuildService(self.database, self.event_bus)
        build_id = build_service.create_build(project["name"], pipeline["id"])
        result = PipelineExecutor(project["path"]).execute(steps)
        build_service.finish_build(
            build_id,
            result["status"],
            json.dumps(result),
            result["exit_code"],
            result["duration"],
        )

        return {
            "build_id": build_id,
            "status": result["status"],
            "project": project["name"],
            "pipeline": pipeline["name"],
            "exit_code": result["exit_code"],
            "duration": result["duration"],
            "steps": result["steps"],
        }

    def _get_project(self, name):
        session = self.database.get_session()
        try:
            project = session.get(Project, name)
            if project is None:
                return None
            return {"name": project.name, "path": project.path}
        finally:
            session.close()

    def delete_pipeline(self, pipeline_id):
        session = self.database.get_session()

        try:
            pipeline = session.get(Pipeline, pipeline_id)

            if pipeline is None:
                raise ValueError(f"Pipeline {pipeline_id} does not exist")

            session.delete(pipeline)
            session.commit()

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()
