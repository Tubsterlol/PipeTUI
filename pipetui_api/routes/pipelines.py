from fastapi import APIRouter, Depends, HTTPException, status

from pipetui_api.dependencies import get_database, get_pipeline_service
from pipetui_api.schemas import PipelineCreate, PipelineRead, PipelineRunResponse
from services.pipeline_service import PipelineService

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("/{pipeline_id}", response_model=PipelineRead)
def get_pipeline(
    pipeline_id: int,
    service: PipelineService = Depends(get_pipeline_service),
):
    pipeline = service.get_pipeline(pipeline_id)
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline


@router.post("", response_model=PipelineRead, status_code=status.HTTP_201_CREATED)
def create_pipeline(
    payload: PipelineCreate,
    service: PipelineService = Depends(get_pipeline_service),
):
    try:
        pipeline_id = service.create_pipeline(payload.project, payload.name)
        for order, step in enumerate(payload.steps, start=1):
            service.add_step(pipeline_id, order, "command", step.command)
        return service.get_pipeline(pipeline_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

@router.delete("/pipelines/{pipeline_id}", status_code=204)
def delete_pipeline(
    pipeline_id: int,
    database=Depends(get_database),
):
    service = PipelineService(database)
    service.delete_pipeline(pipeline_id)


@router.post("/{pipeline_id}/run", response_model=PipelineRunResponse)
def run_pipeline(
    pipeline_id: int,
    service: PipelineService = Depends(get_pipeline_service),
):
    try:
        return service.run_pipeline(pipeline_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
