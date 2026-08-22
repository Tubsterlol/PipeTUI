from datetime import datetime

from storage.models import Pipeline, PipelineStep, Project


class PipelineService:

    def __init__(self, database, event_bus=None):

        self.database = database
        self.event_bus = event_bus

    def create_pipeline(self, project, name):

        session = self.database.get_session()

        try:
            project_exists = session.get(
                Project,
                project
            )

            if project_exists is None:
                raise ValueError(
                    f"Project '{project}' does not exist"
                )

            pipeline = Pipeline(
                project_name=project,
                name=name,
                created_at=datetime.now()
            )

            session.add(pipeline)
            session.commit()

            return pipeline.id

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def add_step(
        self,
        pipeline_id,
        step_order,
        step_type,
        step_value
    ):

        session = self.database.get_session()

        try:
            pipeline = session.get(
                Pipeline,
                pipeline_id
            )

            if pipeline is None:
                raise ValueError(
                    f"Pipeline {pipeline_id} does not exist"
                )

            step = PipelineStep(
                pipeline_id=pipeline_id,
                step_order=step_order,
                step_type=step_type,
                step_value=step_value
            )

            session.add(step)
            session.commit()

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def get_pipeline(self, pipeline_id):

        session = self.database.get_session()

        try:
            pipeline = session.get(
                Pipeline,
                pipeline_id
            )

            return pipeline

        finally:
            session.close()

    def get_pipeline(self, pipeline_id):

        session = self.database.get_session()

        try:
            pipeline = session.get(
                Pipeline,
                pipeline_id
            )

            if pipeline is None:
                return None

            steps = []

            for step in pipeline.steps:

                steps.append({
                    "order": step.step_order,
                    "type": step.step_type,
                    "value": step.step_value
                })

            return {
                "id": pipeline.id,
                "name": pipeline.name,
                "project": pipeline.project_name,
                "created_at": pipeline.created_at,
                "steps": steps
            }

        finally:
            session.close() 