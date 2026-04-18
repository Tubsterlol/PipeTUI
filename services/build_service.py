import subprocess
import time


class BuildService:

    def __init__(self, event_bus, db):
        self.event_bus = event_bus
        self.db = db

    def run_build(self, project_name, project_path, command):

        build_id = self.db.create_build(project_name)

        start = time.time()

        process = subprocess.Popen(
            command,
            cwd=project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        log = ""

        for line in process.stdout:
            log += line
            print(line, end="")

        process.wait()

        duration = round(time.time() - start, 2)

        status = "success" if process.returncode == 0 else "failed"

        self.db.finish_build(build_id, status, log)

        return {
            "status": status,
            "duration": duration,
            "log": log
        }