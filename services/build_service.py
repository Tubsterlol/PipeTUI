import random
from services.log_service import LogService
from services.alert_service import AlertService

class BuildService:

    def __init__(self, event_bus, database):
        self.event_bus = event_bus
        self.database = database
        self.logger = LogService()
        self.alert_service = AlertService(event_bus)

    def run_build(self, project):

        print(f"Running build for {project}")

        self.logger.write_log("info", f"Build started for {project}")

        result = random.choice(["success", "failed"])

        print("Build result:", result)

        self.database.insert_build(project, result)

        if result == "success":
            self.logger.write_log("info", f"Build succeeded for {project}")
        else:
            self.alert_service.alert(
                "build_failure",
                f"Build failed for {project}"
            )

    def show_history(self):

        builds = self.database.get_builds()

        for b in builds:
            print(b)