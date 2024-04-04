from __future__ import annotations

from typing import List, Optional

import msgspec


class PixiInfo(msgspec.Struct, frozen=True, kw_only=True):
    environments_info: List[EnvironmentInfo]
    project_info: Optional[ProjectInfo]


class EnvironmentInfo(msgspec.Struct, frozen=True, kw_only=True):
    name: str
    dependencies: List[str]
    pypi_dependencies: List[str]


class ProjectInfo(msgspec.Struct, frozen=True, kw_only=True):
    manifest_path: str
