import json
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime

from storage.models import Build, Project


@dataclass(frozen=True)
class BuildRecord:
    id: int
    project: str
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    log: str | None
    exit_code: int | None
    duration: float | None

    @property
    def project_name(self):
        return self.project


class BuildService:
    def __init__(self, database, event_bus=None):
        self.database = database
        self.event_bus = event_bus

    def run_build(self, project, project_path, command):
        build_id = self.create_build(project)
        started = time.monotonic()
        try:
            completed = subprocess.run(
                command,
                cwd=project_path,
                capture_output=True,
                text=True,
                check=False,
            )
            output = completed.stdout or ""
            error = completed.stderr or ""
            status = "success" if completed.returncode == 0 else "failed"
            duration = round(time.monotonic() - started, 2)
            self.finish_build(
                build_id,
                status,
                json.dumps(
                    {
                        "status": status,
                        "exit_code": completed.returncode,
                        "duration": duration,
                        "steps": [
                            {
                                "order": 1,
                                "command": " ".join(command),
                                "status": status,
                                "stdout": output,
                                "stderr": error,
                                "exit_code": completed.returncode,
                                "duration": duration,
                            }
                        ],
                    }
                ),
                completed.returncode,
                duration,
            )
            return {
                "status": status,
                "duration": duration,
                "exit_code": completed.returncode,
                "stdout": output,
                "stderr": error,
            }
        except OSError as error:
            message = str(error)
            duration = round(time.monotonic() - started, 2)
            self.finish_build(build_id, "failed", message, 1, duration)
            return {
                "status": "failed",
                "duration": duration,
                "exit_code": 1,
                "stderr": message,
            }

    def create_build(self, project_name):
        session = self.database.get_session()

        try:
            project = session.get(Project, project_name)

            if project is None:
                raise ValueError(f"Project '{project_name}' does not exist")

            build = Build(
                project_name=project_name,
                status="running",
                started_at=datetime.now(),
            )

            session.add(build)
            session.commit()
            session.refresh(build)

            return build.id

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def finish_build(self, build_id, status, log, exit_code=None, duration=None):
        session = self.database.get_session()

        try:
            build = session.get(Build, build_id)

            if build is None:
                raise ValueError(f"Build {build_id} does not exist")

            build.status = status
            build.log = log
            build.finished_at = datetime.now()
            build.exit_code = exit_code
            build.duration = duration

            session.commit()
            return self._record(build)

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def get_builds(self):
        session = self.database.get_session()

        try:
            builds = session.query(Build).order_by(Build.id.desc()).all()

            return [self._record(build) for build in builds]

        finally:
            session.close()

    def get_build(self, build_id):
        session = self.database.get_session()

        try:
            build = session.get(Build, build_id)
            return self._record(build) if build else None

        finally:
            session.close()

    def get_project_builds(self, project):
        session = self.database.get_session()

        try:
            builds = (
                session.query(Build)
                .filter(Build.project_name == project)
                .order_by(Build.id.desc())
                .all()
            )

            return [self._record(build) for build in builds]

        finally:
            session.close()

    @staticmethod
    def _record(build):
        return BuildRecord(
            id=build.id,
            project=build.project_name,
            status=build.status,
            started_at=build.started_at,
            finished_at=build.finished_at,
            log=build.log,
            exit_code=build.exit_code,
            duration=build.duration,
        )
