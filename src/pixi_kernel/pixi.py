from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

import msgspec

from .errors import (
    PIXI_KERNEL_NOT_FOUND,
    PIXI_MANIFEST_NOT_FOUND,
    PIXI_NOT_FOUND,
    PIXI_VERSION_ERROR,
    PIXI_VERSION_NOT_SUPPORTED,
)

logger = logging.getLogger(__name__)
MINIMUM_PIXI_VERSION = "0.21.0"


class PixiDiscoveryError(Exception):
    def __init__(self, message: str):
        self.message = message


class PixiInfo(msgspec.Struct, frozen=True, kw_only=True):
    environments_info: List[EnvironmentInfo]
    project_info: Optional[ProjectInfo]


class EnvironmentInfo(msgspec.Struct, frozen=True, kw_only=True):
    name: str
    dependencies: List[str]
    pypi_dependencies: List[str]


class ProjectInfo(msgspec.Struct, frozen=True, kw_only=True):
    manifest_path: str


def find_pixi_version(kernel_display_name: str) -> Tuple[int, int, int]:
    # Ensure Pixi is in PATH
    if shutil.which("pixi") is None:
        raise PixiDiscoveryError(PIXI_NOT_FOUND.format(kernel_display_name=kernel_display_name))

    # Ensure a supported Pixi version is installed
    result = subprocess.run(["pixi", "--version"], capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.startswith("pixi "):
        raise PixiDiscoveryError(
            PIXI_VERSION_ERROR.format(kernel_display_name=kernel_display_name)
        )

    pixi_version = result.stdout[len("pixi ") :].strip()
    major, minor, patch = map(int, pixi_version.split("."))
    required_major, required_minor, required_patch = map(int, MINIMUM_PIXI_VERSION.split("."))
    if (major, minor, patch) < (required_major, required_minor, required_patch):
        raise PixiDiscoveryError(
            PIXI_VERSION_NOT_SUPPORTED.format(
                kernel_display_name=kernel_display_name,
                minimum_version=MINIMUM_PIXI_VERSION,
            )
        )
    logger.info(f"found Pixi {pixi_version}")
    return (major, minor, patch)


def find_project_manifest(*, cwd: Path, package_name: str, kernel_display_name: str) -> Path:
    # Find project's manifest file
    candidate_dirs = [cwd, *cwd.parents]
    for dir in candidate_dirs:
        for project_filename in ["pixi.toml", "pyproject.toml"]:
            result = subprocess.run(
                ["pixi", "info", f"--manifest-path={project_filename}", "--json"],
                cwd=dir,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logger.error(f"failed to run 'pixi info' for directory {dir}: {result.stderr}")
                continue

            try:
                pixi_info = msgspec.json.decode(result.stdout, type=PixiInfo)
            except msgspec.ValidationError as exception:
                logger.error(f"failed to parse pixi info {result.stdout}: {exception}")
                continue

            if len(pixi_info.environments_info) == 0:
                logger.warning(f"found empty project at {dir}: {pixi_info}")
                continue

            for env in pixi_info.environments_info:
                if env.name == "default" and pixi_info.project_info is not None:
                    if package_name not in env.dependencies + env.pypi_dependencies:
                        logger.error(
                            f"package {package_name} not found in project dependencies {pixi_info}"
                        )
                        raise PixiDiscoveryError(
                            PIXI_KERNEL_NOT_FOUND.format(
                                kernel_display_name=kernel_display_name,
                                package_name=package_name,
                            )
                        )
                    return dir / project_filename

    raise PixiDiscoveryError(PIXI_MANIFEST_NOT_FOUND.format(cwd=cwd))
