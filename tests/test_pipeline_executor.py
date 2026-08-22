import json

from services.build_service import BuildService
from services.pipeline_executor import PipelineExecutor
from storage.database import Database
from storage.models import Project


def test_executor_runs_in_order_and_captures_output(tmp_path):
    executor = PipelineExecutor(str(tmp_path))

    result = executor.execute([
        (1, "command", "python -c \"print('first')\""),
        (2, "command", "python -c \"print('second')\""),
    ])

    assert result["status"] == "success"
    assert [step["order"] for step in result["steps"]] == [1, 2]
    assert "first" in result["steps"][0]["stdout"]
    assert result["steps"][1]["exit_code"] == 0


def test_executor_stops_after_failure(tmp_path):
    executor = PipelineExecutor(str(tmp_path))

    result = executor.execute([
        (1, "command", "python -c \"import sys; sys.exit(7)\""),
        (2, "command", "python -c \"print('must not run')\""),
    ])

    assert result["status"] == "failed"
    assert result["exit_code"] == 7
    assert len(result["steps"]) == 1


def test_pipeline_build_persists_structured_result(tmp_path):
    database = Database("sqlite:///:memory:")
    session = database.get_session()
    session.add(Project(name="test-project", path=str(tmp_path)))
    session.commit()
    session.close()

    build_service = BuildService(database)
    build_id = build_service.create_build("test-project")
    result = PipelineExecutor(str(tmp_path)).execute([
        (1, "command", "python -c \"print('stored')\""),
    ])
    build_service.finish_build(
        build_id,
        result["status"],
        json.dumps(result),
        result["exit_code"],
        result["duration"],
    )

    build = database.get_build_log(build_id)
    assert build[2] == "success"
    assert build[6] == 0
    assert json.loads(build[3])["steps"][0]["stdout"].strip() == "stored"
