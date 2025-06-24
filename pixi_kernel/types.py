from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class PixiInfo(BaseModel):
    environments: list[Environment] = Field(alias="environments_info")
    project: Optional[Project] = Field(alias="project_info")


class Environment(BaseModel):
    name: str
    dependencies: list[str]
    pypi_dependencies: list[str]
    prefix: str


class Project(BaseModel):
    manifest_path: str
