from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from storage.models import Base, Pipeline, PipelineStep, Project


def test_project_creation():
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        project = Project(
            name="test-project",
            path="/tmp/test-project",
        )

        session.add(project)
        session.commit()

        result = session.get(Project, "test-project")

        assert result is not None
        assert result.name == "test-project"
        assert result.path == "/tmp/test-project"


def test_pipeline_relationship():
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        project = Project(
            name="test-project",
            path="/tmp/test-project",
        )

        pipeline = Pipeline(
            name="test-pipeline",
            project=project,
        )

        PipelineStep(
            step_order=1,
            step_type="command",
            step_value="pytest",
            pipeline=pipeline,
        )

        session.add(project)
        session.commit()

        result = session.get(Pipeline, pipeline.id)

        assert result is not None
        assert result.name == "test-pipeline"
        assert result.created_at is not None
        assert len(result.steps) == 1
        assert result.steps[0].step_value == "pytest"
