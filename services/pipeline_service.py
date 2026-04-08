import random
from services.log_service import LogService
from services.alert_service import AlertService

class PipelineService:

    def __init__(self, event_bus, database):

        self.event_bus = event_bus
        self.database = database
        self.logger = LogService()
        self.alert_service = AlertService(event_bus)

    def run_pipeline(self, project):

        print(f"Running pipeline for {project}\n")

        stages = ["Build", "Test", "Package", "Deploy"]

        results = {}

        for stage in stages:

            result = random.choice(["success", "failed"])

            results[stage] = result

            if result == "success":
                print(f"{stage:10} ✓")
                self.logger.write_log("info", f"{stage} succeeded for {project}")

            else:
                print(f"{stage:10} ✗")

                self.alert_service.alert(
                    "pipeline_failure",
                    f"{stage} failed for {project}"
                )

                break

        return results