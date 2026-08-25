from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), primary_key=True)

    path: Mapped[str] = mapped_column(String(1024))

    builds: Mapped[list["Build"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    pipelines: Mapped[list["Pipeline"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    deployments: Mapped[list["Deployment"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Build(Base):
    __tablename__ = "builds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    project_name: Mapped[str] = mapped_column(ForeignKey("projects.name"))

    pipeline_id: Mapped[int | None] = mapped_column(
        ForeignKey("pipelines.id"), nullable=True
    )

    status: Mapped[str] = mapped_column(String(50))

    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    log: Mapped[str | None] = mapped_column(Text, nullable=True)

    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)

    duration: Mapped[float | None] = mapped_column(Float, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="builds")

    pipeline: Mapped["Pipeline | None"] = relationship(back_populates="builds")


class Deployment(Base):
    __tablename__ = "deployments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    project_name: Mapped[str] = mapped_column(ForeignKey("projects.name"))

    environment: Mapped[str] = mapped_column(String(100))

    status: Mapped[str] = mapped_column(String(50))

    project: Mapped["Project"] = relationship(back_populates="deployments")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    type: Mapped[str] = mapped_column(String(100))

    message: Mapped[str] = mapped_column(Text)

    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    project_name: Mapped[str] = mapped_column(ForeignKey("projects.name"))

    name: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="pipelines")

    builds: Mapped[list["Build"]] = relationship(back_populates="pipeline")

    steps: Mapped[list["PipelineStep"]] = relationship(
        back_populates="pipeline",
        order_by="PipelineStep.step_order",
        cascade="all, delete-orphan",
    )


class PipelineStep(Base):
    __tablename__ = "pipeline_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    pipeline_id: Mapped[int] = mapped_column(ForeignKey("pipelines.id"))

    step_order: Mapped[int] = mapped_column(Integer)

    step_type: Mapped[str] = mapped_column(String(100))

    step_value: Mapped[str] = mapped_column(Text)

    pipeline: Mapped["Pipeline"] = relationship(back_populates="steps")
