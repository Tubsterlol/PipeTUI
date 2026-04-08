import click
from services.pipeline_service import PipelineService
from storage.database import Database
from core.event_bus import EventBus

@click.group()
def pipeline():
    pass


@pipeline.command()
@click.argument("project")
def run(project):

    event_bus = EventBus()
    database = Database()

    service = PipelineService(event_bus, database)

    service.run_pipeline(project)