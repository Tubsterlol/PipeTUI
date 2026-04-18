<div align="center">

<pre>
╭─╮╷╭─╮╭─╴╶┬╴╷ ╷╷
├─╯│├─╯├╴  │ │ ││
╵  ╵╵  ╰─╴ ╵ ╰─╯╵
</pre>

</div>

# PipeTUI

A lightweight, terminal-based DevOps dashboard and pipeline controller built with Python. PipeTUI provides a CLI tool for managing CI/CD pipelines with a real-time TUI dashboard for monitoring builds, deployments, alerts, and system health.

> ⚠️ **Linux-Based Only**: PipeTUI is designed and tested exclusively for Linux systems. macOS and Windows are not officially supported.

## Table of Contents

- [Overview](#overview)
  - [Core Capabilities](#core-capabilities)
- [Features](#features)
  - [CLI DevOps Controller](#cli-devops-controller)
  - [Terminal Dashboard (TUI)](#terminal-dashboard-tui)
  - [Database & History](#database--history)
  - [Plugin System](#plugin-system)
- [System Architecture](#system-architecture)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Basic Usage](#basic-usage)
- [Command Reference](#command-reference)
- [Example Workflow](#example-workflow)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [About This Project](#about-this-project)
- [License](#license)

## Overview

PipeTUI is designed as an educational DevOps platform that demonstrates how modern CI/CD tools work. It combines a command-line interface with a live terminal dashboard to give you complete visibility and control over your pipeline operations.

### Core Capabilities

- **Project Management** - Register and manage multiple projects
- **Build Automation** - Trigger builds and track build history
- **Deployment Control** - Deploy applications across different environments
- **Real-Time Monitoring** - Live dashboard with system metrics and activity logs
- **Alert System** - Track pipeline errors and system events
- **Plugin Architecture** - Extensible integrations with Git and Docker

> **Note:** Some pipeline operations are simulated to demonstrate DevOps concepts in an educational environment.

## Features

### CLI DevOps Controller
Command-line interface for managing all pipeline operations:
- Project registration and configuration
- Build triggering and management
- Deployment orchestration
- System control and reset

### Terminal Dashboard (TUI)
Real-time monitoring dashboard displaying:
- **System Health** - CPU and memory usage
- **Build History** - Recent builds and results
- **Deployment Status** - Deployment history and failures
- **System Alerts** - Pipeline errors and warnings
- **Activity Logs** - Recent DevOps operations

### Database & History
All actions are persistently stored in SQLite and displayed in real-time through the dashboard.

### Plugin System
Extensible architecture supporting:
- Git operations (WIP)
- Docker integrations

## System Architecture

PipeTUI is built with a layered architecture for clean separation of concerns:

```
CLI Layer
    ↓
Services Layer (Build, Deploy, Alert, Monitor)
    ↓
Plugin System (Git, Docker, etc.)
    ↓
Database Layer (SQLite)
```

- **CLI Layer** - Handles user commands via Click framework
- **Services Layer** - Implements core business logic (builds, deployments, alerts, monitoring)
- **Plugin System** - Dynamic integration point for external tools
- **Database Layer** - Persistent storage using SQLite
- **Dashboard Layer** - Real-time TUI built with Rich library

## Getting Started

### Installation

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd PipeTUI
pip install -r pyproject.toml
pip install -e .  # Install pipetui command
```

### Basic Usage

#### 1. Register a Project
```bash
pipetui project add myapp /path/to/project
```

#### 2. Run a Build
```bash
pipetui build run myapp
```

#### 3. Deploy to an Environment
```bash
pipetui deploy run myapp dev
```

#### 4. Launch the Dashboard
```bash
pipetui dashboard
```

#### 5. View System Information
```bash
pipetui --help
```

#### 6. Reset System History
```bash
pipetui reset
```

## Command Reference

### Available Commands

```bash
# Project Management
pipetui project add <name> <path>           # Register a new project
pipetui project list                        # List all projects
pipetui project remove <name>               # Remove a project

# Build Operations
pipetui build run <project>                 # Trigger a build
pipetui build list <project>                # List build history
pipetui build status <project>              # Check build status

# Pipeline Operations
pipetui pipeline start <project>            # Start pipeline execution
pipetui pipeline pause <project>            # Pause pipeline execution
pipetui pipeline resume <project>           # Resume pipeline execution
pipetui pipeline status <project>           # Check pipeline status
pipetui pipeline logs <project>             # View pipeline logs

# Deployment Operations
pipetui deploy run <project> <env>          # Deploy to environment (dev/prod)
pipetui deploy status <project>             # Check deployment status
pipetui deploy rollback <project>           # Rollback deployment

# Dashboard & System
pipetui dashboard                           # Launch real-time monitoring dashboard
pipetui --help                              # Display command help
pipetui -v, --version                       # Show version information

# System Management
pipetui reset                                # Clear system history
```

### Man Pages

For detailed command documentation, use the man pages:

```bash
man pipetui                                 # Main manual page
```

## Example Workflow

```bash
# 1. Add a project to the system
pipetui project add myapp /path/to/project

# 2. Start the pipeline
pipetui pipeline start myapp

# 3. Trigger a build
pipetui build run myapp

# 4. Deploy to development environment
pipetui deploy run myapp dev

# 5. Open the dashboard to monitor
pipetui dashboard
```

The dashboard will display:
- System health metrics (CPU, memory)
- Build history and status
- Deployment records
- System alerts and errors
- Recent activity logs

## Technologies Used

- **click** - CLI framework for command parsing
- **rich** - Beautiful terminal user interface
- **psutil** - System resource monitoring
- **SQLite** - Lightweight database
- **Python 3.8+** - Core language

## Project Structure

```
PipeTUI/
├── cli/                 # Command-line interface
├── core/                # Core configuration and event systems
├── services/            # Business logic (builds, deploys, monitoring)
├── plugins/             # Plugin architecture and implementations
├── storage/             # Database layer
├── utils/               # Helper utilities and dashboard
├── docs/                # Documentation
└── Dockerfile           # Container configuration
```

## About This Project

PipeTUI is an educational DevOps learning project that demonstrates core concepts:

- How CI/CD pipelines coordinate builds and deployments
- How DevOps dashboards provide real-time system visibility
- How CLI tools manage infrastructure operations
- How modular plugin architectures enable extensibility

The project simplifies concepts from production tools like Docker, Kubernetes, and Jenkins into a comprehensible, interactive learning environment.

# License
This project is licensed under the [MIT License](LICENSE).
