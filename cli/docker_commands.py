import click
from plugins.docker_plugin import PluginImpl
from services.deploy_service import DeployService
from storage.database import Database
from core.event_bus import EventBus


@click.group()
def docker():
    pass


@docker.command()
@click.argument("project")
@click.argument("environment")
def deploy(project, environment):

    plugin = PluginImpl()

    event_bus = EventBus()
    database = Database()

    service = DeployService(event_bus, database)

    plugin.initialize()

    service.deploy(project, environment, plugin)