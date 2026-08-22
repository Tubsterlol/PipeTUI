from storage.models import Build, Project

class BuildService:

    def __init__(self, database):
        self.database = database

    def create_build(self, project):

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

            build = Build(
                project_name=project,
                status="running"
            )

            session.add(build)
            session.commit()

            return build.id

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def finish_build(self, build_id, status, log):

        session = self.database.get_session()

        try:
            build = session.get(Build, build_id)

            if build is None:
                raise ValueError(
                    f"Build {build_id} does not exist"
                )

            build.status = status
            build.log = log

            session.commit()

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def get_builds(self):

        session = self.database.get_session()

        try:
            builds = (
                session.query(Build)
                .order_by(Build.id.desc())
                .all()
            )

            return builds

        finally:
            session.close()

    def get_build(self, build_id):

        session = self.database.get_session()

        try:
            return session.get(Build, build_id)

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

            return builds

        finally:
            session.close()