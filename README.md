# PipeTUI
A lightweight terminal-based DevOps dashboard and pipeline controller.

PipeTUI is a CLI tool that simulates and manages parts of a CI/CD pipeline environment while providing a real-time Terminal User Interface (TUI) for monitoring builds, deployments, alerts, and system health.

Some pipeline operations in this project are simulated to demonstrate DevOps workflow concepts, allowing the system to behave like a simplified DevOps platform without requiring a full production infrastructure.

# Overview
PipeTUI provides a central control system for DevOps operations through a CLI and a live dashboard.

The tool allows you to:

register projects
run builds
deploy applications to environments
track system alerts
monitor pipeline activity
observe system resource usage
view everything through a live terminal dashboard

Many operations mimic the behavior of real DevOps tools, but certain components such as build execution or deployments may be simulated to demonstrate the workflow of CI/CD systems.

All actions are stored in a database and displayed in real time through the dashboard.

# Features
CLI DevOps Controller

Manage builds, deployments, and projects from a command-line interface.

## Terminal Dashboard (TUI)

A live dashboard displaying:

- CPU usage
- Memory usage
- Build history
- Deployment history
- System alerts
- Recent DevOps activity

### Build Tracking
Record build runs and their results.
Build execution can be simulated to represent a pipeline stage.

### Deployment Tracking
Track deployments across environments such as dev or prod.
Deployments may simulate real deployment processes.

### Alert System
Log and display system alerts such as failed deployments or pipeline errors.

### Plugin Architecture
Supports integrations and simulated services like:

- Git operations
- Docker deployments
### Database Logging
All system activity is recorded and stored for monitoring.

# System Architecture
The project is organized into several layers.

### CLI Layer
Handles user commands and routes them to services.

### Services Layer
Implements system logic such as:

- build execution
- deployments
- alerts
- integrations

### Database Layer
A terminal interface built with the Rich library that displays real-time system information.

### Plugin System
Allows external tools (Git, Docker) to be integrated dynamically.

# Commands
- Add a project.
```bash
python main.py project add <project_name> <project_path>
```

- Run a build.
```bash
python main.py build run <project_name>
```

- Delpy a project.
```bash
python main.py deploy run <project_name> <environment>
```

- Launch Dashboard.
```bash
python main.py dashboard
```
- Reset system history
```bash
python main.py reset
```

- Show command help
```bash
python main.py help
```

# Example Workflow

- Register a project
```bash
python main.py project add myapp /path/to/project
```

- Run a build
```bash
python main.py build run myapp
```

- Deploy the project
```bash
python main.py deploy run myapp dev
```

- Launch the dashboard
```bash
python main.py dashboard
```

### The dashboard will show:

- system health
- builds
- deployments
- alerts
- activity logs

# Technologies Used

Python Libraries:

- click (CLI framework)
- rich (TUI dashboard)
- psutil (system monitoring)
- sqlite (database)

# Purpose of the Project
PipeTUI was built as a DevOps learning project to demonstrate how:

CI/CD pipelines work
DevOps dashboards monitor systems
builds and deployments are tracked
CLI tools coordinate infrastructure tasks

The project mimics concepts used in real DevOps tools like:

- Docker
- Kubernetes
- Jenkins

but in a simplified educational environment.

# License
This project is licensed under the [MIT License](LICENSE).
