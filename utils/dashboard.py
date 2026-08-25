import time

import psutil
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

from storage.database import Database


console = Console()
db = Database()


def system_panel():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent

    text = f"CPU Usage: {cpu}%\nMemory Usage: {memory}%"

    return Panel(text, title="SYSTEM HEALTH")


def alerts_panel():
    alerts = db.get_alerts()[:5]

    if not alerts:
        return Panel("No alerts", title="ALERTS")

    table = Table(show_header=False)
    table.add_column("Type")
    table.add_column("Message")

    for alert in alerts:
        table.add_row(
            str(alert[1]),
            str(alert[2]),
        )

    return Panel(table, title="ALERTS")


def builds_table():
    builds = db.get_builds()[:10]

    table = Table(title="BUILD HISTORY")

    table.add_column("ID")
    table.add_column("Project")
    table.add_column("Status")
    table.add_column("Exit")
    table.add_column("Duration")

    for build in builds:
        build_id = build[4]
        project = build[0]
        status = build[1]
        exit_code = build[6]
        duration = build[7]

        duration_text = f"{duration:.2f}s" if duration is not None else "-"

        table.add_row(
            str(build_id),
            project,
            status.upper(),
            str(exit_code) if exit_code is not None else "-",
            duration_text,
        )

    return table


def deploy_table():
    deployments = db.get_deployments()[:5]

    table = Table(title="DEPLOYMENTS")

    table.add_column("Project")
    table.add_column("Environment")
    table.add_column("Status")

    for deployment in deployments:
        table.add_row(
            str(deployment[0]),
            str(deployment[1]),
            str(deployment[2]),
        )

    if not deployments:
        table.add_row("-", "-", "No deployments")

    return table


def activity_panel():
    builds = db.get_builds()[:5]
    deployments = db.get_deployments()[:5]

    lines = []

    for build in builds:
        lines.append(f"Build #{build[4]} | {build[0]} | {build[1].upper()}")

    for deployment in deployments:
        lines.append(
            f"Deploy #{deployment[3]} | "
            f"{deployment[0]} | "
            f"{deployment[1]} | "
            f"{deployment[2].upper()}"
        )

    if not lines:
        return Panel(
            "No activity yet",
            title="SYSTEM ACTIVITY",
        )

    return Panel(
        "\n".join(lines),
        title="SYSTEM ACTIVITY",
    )


def create_layout():
    layout = Layout()

    layout.split_column(
        Layout(name="top", size=8),
        Layout(name="middle", size=15),
        Layout(name="bottom"),
    )

    layout["top"].split_row(
        Layout(name="system"),
        Layout(name="alerts"),
    )

    layout["middle"].split_row(
        Layout(name="builds"),
        Layout(name="deployments"),
    )

    return layout


def start_dashboard():
    layout = create_layout()

    with Live(
        layout,
        refresh_per_second=1,
        screen=True,
    ):
        while True:
            layout["system"].update(system_panel())

            layout["alerts"].update(alerts_panel())

            layout["builds"].update(builds_table())

            layout["deployments"].update(deploy_table())

            layout["bottom"].update(activity_panel())

            time.sleep(2)
