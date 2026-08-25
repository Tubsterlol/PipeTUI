# PipeTUI

PipeTUI is a local DevOps command-line tool for registering projects, running builds, executing simple pipelines, deploying applications, and inspecting the resulting history from a terminal.

It is primarily an educational project. Builds and deployments are recorded in a local SQLite database, while Docker deployment is available through the Docker plugin.

## What it provides

- Project registration and project information
- Automatic build command detection for `package.json`, `Makefile`, and `build.py`
- Build history, logs, and live log streaming
- Simple build-and-deploy pipelines
- Deployment history and Docker-backed deployment commands
- Alerts and filtered application logs
- A live Rich dashboard with CPU, memory, build, deployment, and alert panels
- A plugin architecture for integrations such as Git and Docker

## Requirements

- Python 3.8 or newer
- Linux is the supported and tested platform
- Docker is required only for Docker deployments
- Node.js/npm, GNU Make, or Python may be required by the build system detected in a registered project

## Installation

```bash
git clone <repository-url>
cd PipeTUI
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install rich psutil
```

The last command installs the dashboard dependencies. They are currently imported by the application but are not yet declared in `pyproject.toml`.

The editable install exposes the `pipetui` command:

```bash
pipetui --help
pipetui --version
```

## Quick start

Register a project, run its build, and inspect the result:

```bash
pipetui project add myapp /path/to/myapp
pipetui project list
pipetui project info myapp
pipetui build run myapp
pipetui build history
```

Create and run the default three-step pipeline (`pytest`, `ruff check .`, and `ruff format --check .`):

```bash
pipetui pipeline create myapp
pipetui pipeline run myapp
# or: pipetui pipeline run default
```

Every pipeline run creates a persistent build. Steps execute in order and stop at the first failure. Output, errors, exit codes, and durations are stored with the build.

Create a named pipeline with custom commands:

```bash
pipetui pipeline create myapp my-pipeline \
  --step "pytest" \
  --step "ruff check ." \
  --step "ruff format --check ."
pipetui pipeline run my-pipeline
```

Launch the live dashboard in a separate terminal:

```bash
pipetui dashboard
```

## Command reference

### System

```text
pipetui start                         Start the monitoring service
pipetui status                        Show system status
pipetui reset                         Clear build, deployment, and alert history
pipetui dashboard                     Launch the live terminal dashboard
```

### Projects

```text
pipetui project add <name> <path>     Register a project directory
pipetui project list                  List registered projects
pipetui project info <name>           Show project, build, and deployment details
```

### Builds

```text
pipetui build run <project>           Detect and run the project's build command
pipetui build history                 Show build history
pipetui build list                    Alias for build history
pipetui build show-logs <project>     List logs for a project's builds
pipetui build show-logs <project> --last
                                      Show the latest build log
pipetui build show-logs <project> --id <id>
                                      Show a build log by ID
pipetui build tail <project>          Stream the latest build log
```

Build detection checks for these files in order:

| Detected file  | Command           |
| -------------- | ----------------- |
| `package.json` | `npm run build`   |
| `Makefile`     | `make`            |
| `build.py`     | `python build.py` |

If none is found, PipeTUI records a command that prints `No build system detected`.

### Deployments and pipelines

```text
pipetui deploy run <project> <environment>
pipetui deploy history
pipetui docker deploy <project> <environment>

pipetui pipeline create <project>     Create the default build/deploy pipeline
pipetui pipeline run <project>        Run a project's pipeline
```

`docker deploy` uses the Docker plugin to build an image from the registered project directory and start a container. The Docker daemon and Docker CLI must be available for this command.

### Alerts and logs

```text
pipetui alerts show                   Show recorded alerts
pipetui alerts clear                  Delete recorded alerts
pipetui logs show                     Show application logs
pipetui logs filter <level>           Filter logs, e.g. INFO or ERROR
pipetui logs build <id>               Show structured output for a build
```

## Data and architecture

By default, PipeTUI creates `devops.db` in the PipeTUI project directory, regardless of the current working directory. The database stores projects, builds, deployments, alerts, pipelines, and pipeline steps.

```text
cli/       Click commands and command wiring
core/      Configuration and event bus
services/  Build, deployment, pipeline, monitoring, alert, and log logic
plugins/   Git/Docker plugin implementations and plugin loading
storage/   SQLAlchemy models and SQLite access
utils/     Dashboard and shared helpers
tests/     Service and model tests
docs/      Manual page source
```

## Development

Run the test suite with:

```bash
python -m pytest
```

Run the CLI directly from the repository when needed:

```bash
python -m cli.main --help
```

The project uses Click for the CLI, SQLAlchemy for persistence, Rich for terminal rendering, and psutil for system metrics.

## Limitations

PipeTUI is a local learning tool rather than a production CI/CD system. It does not provide remote workers, credentials management, deployment approvals, or distributed execution. Review commands carefully before running them against a real project or Docker host.

## License

PipeTUI is released under the [MIT License](LICENSE).
