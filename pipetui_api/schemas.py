from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    path: str = Field(min_length=1, max_length=1024)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    path: str


class PipelineStepCreate(BaseModel):
    command: str = Field(min_length=1)


class PipelineCreate(BaseModel):
    project: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    steps: list[PipelineStepCreate] = Field(default_factory=list)


class PipelineStepRead(BaseModel):
    id: int
    order: int
    type: str
    value: str


class PipelineRead(BaseModel):
    id: int
    name: str
    project: str
    created_at: datetime | None
    steps: list[PipelineStepRead]


class PipelineRunResponse(BaseModel):
    build_id: int
    status: str
    project: str
    pipeline: str
    exit_code: int
    duration: float
    steps: list[dict]


class BuildRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project: str
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    log: str | None
    exit_code: int | None
    duration: float | None
