class DashboardService:
    def __init__(self, database):
        self.database = database

    def get_builds(self):
        return self.database.get_builds()

    def get_deployments(self):
        return self.database.get_deployments()

    def get_alerts(self):
        return self.database.get_alerts()
