import time
import psutil

from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live

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

    text = ""

    for a in alerts:
        text += f"{a[1]}\n"

    if text == "":
        text = "No alerts"

    return Panel(text, title="ALERTS")


def builds_table():

    builds = db.get_builds()

    table = Table(title="Build History")

    table.add_column("Project")
    table.add_column("Status")

    for b in builds:
        table.add_row(str(b[0]), str(b[1]))

    return table


def deploy_table():

    table = Table()

    table.add_column("Project")
    table.add_column("Environment")
    table.add_column("Status")

    deployments = db.get_deployments()[:5]

    for d in deployments:
        table.add_row(str(d[0]), str(d[1]), str(d[2]))

    return Panel(table, title="DEPLOYMENTS")


def activity_panel():

    builds = db.get_builds()[:3]
    deploys = db.get_deployments()[:3]

    text = ""

    for b in builds:
        text += f"Build {b[1]} for {b[0]}\n"

    for d in deploys:
        text += f"Deploy {d[2]} for {d[0]} ({d[1]})\n"

    if text == "":
        text = "No activity yet"

    return Panel(text, title="SYSTEM ACTIVITY")


def create_layout():

    layout = Layout()

    layout.split_column(
        Layout(name="top", size=8),
        Layout(name="middle", size=12),
        Layout(name="bottom")
    )

    layout["top"].split_row(
        Layout(name="system"),
        Layout(name="alerts")
    )

    layout["middle"].split_row(
        Layout(name="builds"),
        Layout(name="deployments")
    )

    return layout


def start_dashboard():

    layout = create_layout()

    with Live(layout, refresh_per_second=1, screen=True):

        while True:

            layout["system"].update(system_panel())
            layout["alerts"].update(alerts_panel())

            layout["builds"].update(builds_table())
            layout["deployments"].update(deploy_table())

            layout["bottom"].update(activity_panel())

            time.sleep(2)