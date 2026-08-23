from fastapi import APIRouter, Depends, HTTPException

from pipetui_api.dependencies import get_build_service
from pipetui_api.schemas import BuildRead
from services.build_service import BuildService

router = APIRouter(prefix="/builds", tags=["builds"])


@router.get("", response_model=list[BuildRead])
def list_builds(service: BuildService = Depends(get_build_service)):
    return service.get_builds()


@router.get("/{build_id}", response_model=BuildRead)
def get_build(
    build_id: int,
    service: BuildService = Depends(get_build_service),
):
    build = service.get_build(build_id)
    if build is None:
        raise HTTPException(status_code=404, detail="Build not found")
    return build
