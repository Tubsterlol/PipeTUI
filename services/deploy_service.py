import random
from services.log_service import LogService

class DeployService:

    def __init__(self, event_bus, database):
        self.event_bus = event_bus
        self.database = database
        self.logger = LogService()

    def deploy(self, project, environment):

        print(f"Deploying {project} to {environment}")

        self.logger.write_log("info", f"Deployment started for {project} to {environment}")

        result = random.choice(["success", "failed"])

        print("Deployment result:", result)

        self.database.insert_deployment(project, environment, result)

        if result == "success":
            self.logger.write_log("info", f"Deployment success for {project}")
        else:
            self.logger.write_log("error", f"Deployment failed for {project}")
            self.event_bus.publish("deploy_failed", project)