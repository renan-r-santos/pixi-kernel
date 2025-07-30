from __future__ import annotations

from typing import Optional

import msgspec


class PixiInfo(msgspec.Struct, frozen=True, kw_only=True):
    environments: list[Environment] = msgspec.field(name="environments_info")
    project: Optional[Project] = msgspec.field(name="project_info")


class Environment(msgspec.Struct, frozen=True, kw_only=True):
    name: str
    dependencies: list[str]
    pypi_dependencies: list[str]
    prefix: str


class Project(msgspec.Struct, frozen=True, kw_only=True):
    manifest_path: str
