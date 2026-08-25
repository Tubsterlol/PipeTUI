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
- A read-only Rich dashboard for projects, pipelines, builds, and activity
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
# Optional
python -m venv .venv
source .venv/bin/activate
#
python -m pip install --upgrade pip
python -m pip install -e .
```

All runtime dependencies are installed by the editable install.

The editable install exposes the `pipetui` command:

```bash
pipetui --help
pipetui --version
```

## Example workflow

PipeTUI keeps mutations in the CLI. The Rich TUI is an observation dashboard and can run in a separate terminal.

Register a project and inspect the project list:

```bash
pipetui project add my-api /path/to/my-api
pipetui project list
```

Create an empty pipeline, then add its steps in order:

```bash
pipetui pipeline create my-api ci
pipetui step add my-api ci 1 "pytest"
pipetui step add my-api ci 2 "ruff check ."
pipetui step add my-api ci 3 "ruff format --check ."
pipetui step list my-api ci
```

Edit or remove a step without executing it:

```bash
pipetui step edit my-api ci 2 "ruff check --output-format=concise"
pipetui step delete my-api ci 3
```

Run the pipeline and inspect its build:

```bash
pipetui pipeline run my-api ci
pipetui build list my-api
pipetui build logs 12
```

In another terminal, start the read-only dashboard before or during execution:

```bash
pipetui tui
```

Every pipeline run creates a persistent build. Steps execute in order and stop at the first failure. Output, errors, exit codes, durations, and the source pipeline are stored with the build.

## Command reference

### System

```text
pipetui start                         Start the monitoring service
pipetui status                        Show system status
pipetui reset                         Clear build, deployment, and alert history
pipetui tui                            Launch the read-only Rich dashboard
```

### Projects

```text
pipetui project add <name> <path>     Register a project directory
pipetui project list                  List registered projects
pipetui project edit <name>           Change path or name with --path/--name
pipetui project delete <name>         Delete a project and related data
```

Deleting a project cascades to its pipelines, steps, builds, logs, and deployments. Deleting a pipeline leaves existing builds as historical records.

### Builds

```text
pipetui build run <project>           Detect and run the project's build command
pipetui build list [<project>]        Show build history
pipetui build history                 Alias for build list
pipetui build show-logs <project>     List logs for a project's builds
pipetui build show-logs <project> --last
                                      Show the latest build log
pipetui build show-logs <project> --id <id>
                                      Show a build log by ID
pipetui build logs <id>               Show output for a build ID
pipetui build tail <project>          Stream the latest build log
```

Build detection checks for these files in order:

| Detected file  | Command           |
| -------------- | ----------------- |
| `package.json` | `npm run build`   |
| `Makefile`     | `make`            |
| `build.py`     | `python build.py` |

If none is found, PipeTUI records a command that prints `No build system detected`.

### Pipelines and steps

```text
pipetui pipeline list <project>                 List pipelines
pipetui pipeline create <project> [<name>]      Create an empty pipeline
pipetui pipeline edit <project> <name> --name <new-name>
                                                  Rename a pipeline
pipetui pipeline delete <project> <name>         Delete a pipeline
pipetui pipeline run <project> <name>            Execute a pipeline

pipetui step list <project> <pipeline>           List pipeline steps
pipetui step add <project> <pipeline> <order> <command>
                                                  Append a command step
pipetui step edit <project> <pipeline> <order> <command>
                                                  Edit a command step
pipetui step delete <project> <pipeline> <order> Delete a step
```

### Deployments

```text
pipetui deploy run <project> <environment>       Deploy a project
pipetui deploy history                           Show deployment history
```

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
utils/     Shared helpers
tui/       Read-only Rich observation dashboard
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

The project uses Click for CLI control, SQLAlchemy for persistence, and Rich for terminal rendering. The CLI handles input, validation, CRUD, execution, and errors; the TUI only reads and displays stored state.

## Limitations

PipeTUI is a local learning tool rather than a production CI/CD system. It does not provide remote workers, credentials management, deployment approvals, or distributed execution. Review commands carefully before running them against a real project or Docker host.

## License

PipeTUI is released under the [MIT License](LICENSE).
