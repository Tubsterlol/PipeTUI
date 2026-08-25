import shlex
import subprocess
import time


class PipelineExecutor:
    """Execute pipeline command steps without invoking a shell."""

    def __init__(self, project_path):
        self.project_path = project_path

    def execute(self, steps):
        started = time.monotonic()
        results = []
        status = "success"
        exit_code = 0

        for order, step_type, command in steps:
            step_started = time.monotonic()
            if step_type != "command":
                result = {
                    "order": order,
                    "command": command,
                    "status": "failed",
                    "stdout": "",
                    "stderr": f"Unsupported step type: {step_type}",
                    "exit_code": 2,
                    "duration": 0.0,
                }
            else:
                try:
                    argv = shlex.split(command, posix=True)
                    if not argv:
                        raise ValueError("command is empty")
                    completed = subprocess.run(
                        argv,
                        cwd=self.project_path,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    result = {
                        "order": order,
                        "command": command,
                        "status": "success" if completed.returncode == 0 else "failed",
                        "stdout": completed.stdout or "",
                        "stderr": completed.stderr or "",
                        "exit_code": completed.returncode,
                    }
                except (OSError, ValueError) as error:
                    result = {
                        "order": order,
                        "command": command,
                        "status": "failed",
                        "stdout": "",
                        "stderr": str(error),
                        "exit_code": 1,
                    }

            result["duration"] = round(time.monotonic() - step_started, 2)
            results.append(result)
            if result["status"] == "failed":
                status = "failed"
                exit_code = result["exit_code"]
                break

        return {
            "status": status,
            "exit_code": exit_code,
            "duration": round(time.monotonic() - started, 2),
            "steps": results,
        }
