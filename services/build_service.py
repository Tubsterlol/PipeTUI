import random
from services.log_service import LogService

class BuildService:

    def __init__(self, event_bus, database):
        self.event_bus = event_bus
        self.database = database
        self.logger = LogService()

    def run_build(self, project):

        print(f"Running build for {project}")

        self.logger.write_log("info", f"Build started for {project}")

        result = random.choice(["success", "failed"])

        print("Build result:", result)

        self.database.insert_build(project, result)

        if result == "success":
            self.logger.write_log("info", f"Build succeeded for {project}")
        else:
            self.logger.write_log("error", f"Build failed for {project}")
            self.event_bus.publish("build_failed", project)

    def show_history(self):

        builds = self.database.get_builds()

        for b in builds:
            print(b)