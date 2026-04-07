class AlertService:

    def __init__(self, event_bus):

        event_bus.subscribe("cpu_high", self.cpu_alert)
        event_bus.subscribe("memory_high", self.memory_alert)
        event_bus.subscribe("build_failed", self.build_failed)
        event_bus.subscribe("deploy_failed", self.deploy_failed)

    def cpu_alert(self, cpu):
        print(f"[ALERT] High CPU Usage: {cpu}%")

    def memory_alert(self, memory):
        print(f"[ALERT] High Memory Usage: {memory}%")

    def build_failed(self, project):
        print(f"[ALERT] Build failed for {project}")

    def deploy_failed(self, project):
        print(f"[ALERT] Deployment failed for {project}")