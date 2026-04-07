from datetime import datetime
from storage.database import Database

class AlertService:

    def __init__(self, event_bus=None):
        self.db = Database()
        self.event_bus = event_bus

    def alert(self, alert_type, message):

        timestamp = str(datetime.now())

        print(f"[ALERT] {message}")

        self.db.insert_alert(alert_type, message, timestamp)