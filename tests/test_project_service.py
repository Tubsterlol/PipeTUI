from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.project_service import ProjectService
from storage.models import Base


class DatabaseForTest:
    def __init__(self):
        self.engine = create_engine("sqlite:///:memory:")

        self.Session = sessionmaker(bind=self.engine)

        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()


def test_add_project(tmp_path):
    database = DatabaseForTest()

    service = ProjectService(database)

    project_path = tmp_path / "project"
    project_path.mkdir()

    service.add_project("test-project", str(project_path))

    projects = service.list_projects()

    assert len(projects) == 1
    assert projects[0].name == "test-project"
    assert projects[0].path == str(project_path)


def test_get_project_path(tmp_path):
    database = DatabaseForTest()

    service = ProjectService(database)

    project_path = tmp_path / "project"
    project_path.mkdir()

    service.add_project("test-project", str(project_path))

    result = service.get_project_path("test-project")

    assert result == str(project_path)
