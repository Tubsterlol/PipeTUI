from fastapi.testclient import TestClient
from pipetui_api.dependencies import get_database
from pipetui_api.main import app

from storage.database import Database


def test_pipeline_api_creates_and_runs_build(tmp_path):
    project_path = tmp_path / "project"
    project_path.mkdir()
    database = Database(f"sqlite:///{tmp_path / 'api.db'}")

    def override_database():
        yield database

    app.dependency_overrides[get_database] = override_database
    client = TestClient(app)

    try:
        project_response = client.post(
            "/projects",
            json={"name": "api-project", "path": str(project_path)},
        )
        assert project_response.status_code == 201

        pipeline_response = client.post(
            "/pipelines",
            json={
                "project": "api-project",
                "name": "test-pipeline",
                "steps": [{"command": "python -c \"print('api')\""}],
            },
        )
        assert pipeline_response.status_code == 201
        pipeline_id = pipeline_response.json()["id"]

        run_response = client.post(f"/pipelines/{pipeline_id}/run")
        assert run_response.status_code == 200
        assert run_response.json()["status"] == "success"

        build_id = run_response.json()["build_id"]
        build_response = client.get(f"/builds/{build_id}")
        assert build_response.status_code == 200
        assert build_response.json()["project"] == "api-project"
        assert build_response.json()["status"] == "success"
    finally:
        app.dependency_overrides.clear()
        database.close()
