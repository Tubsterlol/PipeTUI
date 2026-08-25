import subprocess


class PluginImpl:
    name = "Docker Deployment"

    def initialize(self):
        print("Docker plugin initialized")

    def deploy(self, project, project_path):
        image_name = f"{project}:latest"

        try:
            print(f"Building Docker image for {project}")

            subprocess.run(
                ["docker", "build", "-t", image_name, project_path], check=True
            )

            print(f"Running container {project}")

            subprocess.run(
                ["docker", "run", "-d", "--name", project, image_name], check=True
            )

            return "success"

        except (subprocess.CalledProcessError, FileNotFoundError):
            return "failed"
