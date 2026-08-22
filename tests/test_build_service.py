from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.build_service import BuildService
from storage.models import Base, Project


class DatabaseForTest:

    def __init__(self):

        self.engine = create_engine(
            "sqlite:///:memory:"
        )

        self.Session = sessionmaker(
            bind=self.engine
        )

        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()


def add_project(database):

    session = database.get_session()

    project = Project(
        name="test-project",
        path="/tmp/test-project"
    )

    session.add(project)
    session.commit()

    session.close()


def test_create_build():

    database = DatabaseForTest()

    add_project(database)

    service = BuildService(database)

    build_id = service.create_build(
        "test-project"
    )

    build = service.get_build(build_id)

    assert build is not None
    assert build.project_name == "test-project"
    assert build.status == "running"


def test_finish_build():

    database = DatabaseForTest()

    add_project(database)

    service = BuildService(database)

    build_id = service.create_build(
        "test-project"
    )

    service.finish_build(
        build_id,
        "success",
        "Build completed successfully"
    )

    build = service.get_build(build_id)

    assert build.status == "success"
    assert build.log == "Build completed successfully"


def test_get_project_builds():

    database = DatabaseForTest()

    add_project(database)

    service = BuildService(database)

    service.create_build("test-project")
    service.create_build("test-project")

    builds = service.get_project_builds(
        "test-project"
    )

    assert len(builds) == 2

def test_create_build_for_missing_project():

    database = DatabaseForTest()

    service = BuildService(database)

    try:
        service.create_build("missing-project")
        assert False
    except ValueError as error:
        assert str(error) == (
            "Project 'missing-project' does not exist"
        )