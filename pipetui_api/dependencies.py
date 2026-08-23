from collections.abc import Generator

from fastapi import Depends

from services.build_service import BuildService
from services.pipeline_service import PipelineService
from services.project_service import ProjectService
from storage.database import Database


def get_database() -> Generator[Database, None, None]:
    database = Database()
    try:
        yield database
    finally:
        database.close()


def get_project_service(database: Database = Depends(get_database)) -> ProjectService:
    return ProjectService(database)


def get_build_service(database: Database = Depends(get_database)) -> BuildService:
    return BuildService(database)


def get_pipeline_service(database: Database = Depends(get_database)) -> PipelineService:
    return PipelineService(database)
