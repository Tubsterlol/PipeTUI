import random
from services.log_service import LogService
from services.alert_service import AlertService

class DeployService:

    def __init__(self, event_bus, database):
        self.event_bus = event_bus
        self.database = database
        self.logger = LogService()
        self.alert_service = AlertService(event_bus)

    def deploy(self, project, environment, plugin=None):

        print(f"Deploying {project} to {environment}")

        if plugin:
            result = plugin.deploy(project)
        else:
            result = random.choice(["success", "failed"])

        print("Deployment result:", result)

        self.database.insert_deployment(project, environment, result)

        if result == "success":
            self.logger.write_log("info", f"Deployment success for {project}")
        else:
            self.alert_service.alert(
                "deploy_failure",
                f"Deployment failed for {project}"
            )
