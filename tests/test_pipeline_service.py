from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.pipeline_service import PipelineService
from storage.models import Base, Project


class DatabaseForTest:
    def __init__(self):
        self.engine = create_engine("sqlite:///:memory:")

        self.Session = sessionmaker(bind=self.engine)

        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()


def add_project(database):
    session = database.get_session()

    project = Project(name="test-project", path="/tmp/test-project")

    session.add(project)
    session.commit()

    session.close()


def test_create_pipeline():
    database = DatabaseForTest()

    add_project(database)

    service = PipelineService(database)

    pipeline_id = service.create_pipeline("test-project", "test-pipeline")

    pipeline = service.get_pipeline(pipeline_id)

    assert pipeline is not None
    assert pipeline["name"] == "test-pipeline"
    assert pipeline["project"] == "test-project"


def test_create_pipeline_for_missing_project():
    database = DatabaseForTest()

    service = PipelineService(database)

    try:
        service.create_pipeline("missing-project", "test-pipeline")

        assert False

    except ValueError as error:
        assert str(error) == ("Project 'missing-project' does not exist")


def test_add_pipeline_step():
    database = DatabaseForTest()

    add_project(database)

    service = PipelineService(database)

    pipeline_id = service.create_pipeline("test-project", "test-pipeline")

    service.add_step(pipeline_id, 1, "command", "pytest")

    pipeline = service.get_pipeline(pipeline_id)

    assert pipeline is not None
    assert len(pipeline["steps"]) == 1

    step = pipeline["steps"][0]

    assert step["order"] == 1
    assert step["type"] == "command"
    assert step["value"] == "pytest"


def test_pipeline_steps_are_ordered():
    database = DatabaseForTest()

    add_project(database)

    service = PipelineService(database)

    pipeline_id = service.create_pipeline("test-project", "test-pipeline")

    service.add_step(pipeline_id, 2, "command", "pytest")

    service.add_step(pipeline_id, 1, "command", "ruff check .")

    pipeline = service.get_pipeline(pipeline_id)

    assert pipeline is not None
    assert len(pipeline["steps"]) == 2

    assert pipeline["steps"][0]["order"] == 1
    assert pipeline["steps"][0]["value"] == "ruff check ."

    assert pipeline["steps"][1]["order"] == 2
    assert pipeline["steps"][1]["value"] == "pytest"
