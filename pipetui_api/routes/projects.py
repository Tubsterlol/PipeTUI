from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from pipetui_api.dependencies import get_project_service
from pipetui_api.schemas import ProjectCreate, ProjectRead
from services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def list_projects(service: ProjectService = Depends(get_project_service)):
    return service.list_projects()


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
):
    try:
        return service.add_project(payload.name, payload.path)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except IntegrityError as error:
        raise HTTPException(status_code=409, detail="Project already exists") from error
