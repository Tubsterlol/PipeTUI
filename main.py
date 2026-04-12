from cli.command_handler import cli, reset, help
from plugins.plugin_manager import PluginManager
from cli.alert_commands import alerts
from cli.dashboard_commands import dashboard
from cli.pipeline_commands import pipeline
from cli.docker_commands import docker
from cli.project_commands import project


def load_plugins():

    manager = PluginManager()
    manager.load_plugins()
    cli.add_command(pipeline)

cli.add_command(alerts)
cli.add_command(dashboard)
cli.add_command(docker)
cli.add_command(project)
cli.add_command(reset)
cli.add_command(help)

if __name__ == "__main__":

    load_plugins()

    cli()
