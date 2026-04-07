import os
from datetime import datetime

class LogService:

    def __init__(self):
        self.log_file = "logs/system.log"

        if not os.path.exists("logs"):
            os.makedirs("logs")

    def write_log(self, level, message):

        timestamp = datetime.now()

        log = f"[{timestamp}] [{level.upper()}] {message}\n"

        with open(self.log_file, "a") as f:
            f.write(log)

    def show_logs(self):

        with open(self.log_file, "r") as f:
            for line in f:
                print(line.strip())

    def filter_logs(self, level):

        with open(self.log_file, "r") as f:
            for line in f:
                if f"[{level.upper()}]" in line:
                    print(line.strip())