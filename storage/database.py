from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from storage.models import (
    Alert,
    Base,
    Build,
    Deployment,
    Pipeline,
    PipelineStep,
    Project,
)


class Database:

    def __init__(self, database_url="sqlite:///devops.db"):

        self.engine = create_engine(database_url)

        self.Session = sessionmaker(
            bind=self.engine
        )

        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

    def close(self):
        self.engine.dispose()

    def get_project(self, name):
        with self.get_session() as session:
            project = session.get(Project, name)
            if project is None:
                return None
            return {"name": project.name, "path": project.path}

    def get_projects(self):
        with self.get_session() as session:
            return [(p.name, p.path) for p in session.query(Project).order_by(Project.name)]

    def add_project(self, name, path):
        with self.get_session() as session:
            session.add(Project(name=name, path=path))
            session.commit()

    def get_builds(self):
        with self.get_session() as session:
            builds = session.query(Build).order_by(Build.id.desc()).all()
            return [
                (b.project_name, b.status, b.started_at, b.finished_at, b.id, b.log)
                for b in builds
            ]

    def get_project_builds(self, project):
        with self.get_session() as session:
            builds = (
                session.query(Build)
                .filter(Build.project_name == project)
                .order_by(Build.id.desc())
                .all()
            )
            return [
                (b.id, b.project_name, b.status, b.started_at, b.finished_at, b.log)
                for b in builds
            ]

    def get_last_build(self, project):
        builds = self.get_project_builds(project)
        if not builds:
            return None
        b = builds[0]
        return (b[2], b[3].isoformat() if b[3] else None,
                b[4].isoformat() if b[4] else None, b[1], b[0], b[5] or "")

    def get_build_log(self, build_id):
        with self.get_session() as session:
            b = session.get(Build, int(build_id))
            if b is None:
                return None
            return (b.id, b.project_name, b.status, b.log or "", b.started_at, b.finished_at)

    def get_last_build_log(self, project):
        build = self.get_last_build(project)
        return (project, build[5]) if build else None

    def get_deployments(self):
        with self.get_session() as session:
            deployments = session.query(Deployment).order_by(Deployment.id.desc()).all()
            return [(d.project_name, d.environment, d.status, d.id) for d in deployments]

    def get_last_deployment(self, project):
        deployments = [d for d in self.get_deployments() if d[0] == project]
        return deployments[0] if deployments else None

    def insert_deployment(self, project, environment, status):
        with self.get_session() as session:
            session.add(Deployment(project_name=project, environment=environment, status=status))
            session.commit()

    def get_alerts(self):
        with self.get_session() as session:
            alerts = session.query(Alert).order_by(Alert.id.desc()).all()
            return [(a.id, a.type, a.message, a.timestamp) for a in alerts]

    def insert_alert(self, alert_type, message, timestamp=None):
        with self.get_session() as session:
            session.add(Alert(type=alert_type, message=message))
            session.commit()

    def clear_alerts(self):
        with self.get_session() as session:
            session.query(Alert).delete()
            session.commit()

    def get_build_stats(self, project):
        builds = self.get_project_builds(project)
        total = len(builds)
        successful = sum(1 for b in builds if b[2] == "success")
        return total, successful

    def create_pipeline(self, project, name):
        with self.get_session() as session:
            if session.get(Project, project) is None:
                raise ValueError(f"Project '{project}' does not exist")
            pipeline = Pipeline(project_name=project, name=name)
            session.add(pipeline)
            session.commit()
            return pipeline.id

    def add_pipeline_step(self, pipeline_id, step_order, step_type, step_value):
        with self.get_session() as session:
            if session.get(Pipeline, pipeline_id) is None:
                raise ValueError(f"Pipeline {pipeline_id} does not exist")
            session.add(PipelineStep(
                pipeline_id=pipeline_id,
                step_order=step_order,
                step_type=step_type,
                step_value=step_value,
            ))
            session.commit()

    def get_pipeline_steps(self, project):
        with self.get_session() as session:
            rows = (
                session.query(PipelineStep.step_order, PipelineStep.step_type, PipelineStep.step_value)
                .join(Pipeline, Pipeline.id == PipelineStep.pipeline_id)
                .filter(Pipeline.project_name == project)
                .order_by(PipelineStep.step_order)
                .all()
            )
            return list(rows)

    def reset_history(self):
        with self.get_session() as session:
            session.query(Build).delete()
            session.query(Deployment).delete()
            session.query(Alert).delete()
            session.commit()
