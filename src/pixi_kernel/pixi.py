from __future__ import annotations

import logging
import shutil
from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE, Process
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, ValidationError

from .errors import PIXI_KERNEL_NOT_FOUND, PIXI_NOT_FOUND, PIXI_OUTDATED, PIXI_VERSION_ERROR

MINIMUM_PIXI_VERSION = "0.30.0"

logger = logging.getLogger(__name__)


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


async def subprocess_exec(program: str, *args: str, **kwargs: Any) -> tuple[Process, str, str]:
    process = await create_subprocess_exec(program, *args, stdout=PIPE, stderr=PIPE, **kwargs)
    stdout_bytes, stderr_bytes = await process.communicate()
    stdout, stderr = stdout_bytes.decode("utf-8"), stderr_bytes.decode("utf-8")
    return process, stdout, stderr


async def ensure_readiness(
    *,
    cwd: Path,
    env: dict[str, str],
    required_package: str,
    kernel_name: str,
) -> Environment:
    """Ensure the Pixi environment is ready to run the kernel.

    This function checks the following:
        - Ensure Pixi is installed and in PATH
        - Ensure the installed Pixi version is supported
        - Ensure there is a Pixi project in the current working directory or any of its parents
        - Ensure the Pixi project is valid and has a default environment
        - Ensure the required kernel package is a project dependency

    If any of the checks fail, a RuntimeError is raised and JupterLab will display a dialog with
    the error message.

    Returns the path to the Pixi environment prefix.
    """
    # Remove PIXI_IN_SHELL for when JupyterLab is started from a Pixi shell
    # https://github.com/renan-r-santos/pixi-kernel/issues/35
    env.pop("PIXI_IN_SHELL", None)

    # Ensure Pixi is in PATH
    if shutil.which("pixi") is None:
        raise RuntimeError(PIXI_NOT_FOUND.format(kernel_name=kernel_name))

    # Ensure a supported Pixi version is installed
    process, stdout, stderr = await subprocess_exec("pixi", "--version")
    if process.returncode != 0 or not stdout.startswith("pixi "):
        raise RuntimeError(PIXI_VERSION_ERROR.format(kernel_name=kernel_name))

    # Parse Pixi version and check it against the minimum required version
    pixi_version = stdout[len("pixi ") :].strip()

    major, minor, patch = map(int, pixi_version.split("."))
    required_major, required_minor, required_patch = map(int, MINIMUM_PIXI_VERSION.split("."))

    if (major, minor, patch) < (required_major, required_minor, required_patch):
        raise RuntimeError(
            PIXI_OUTDATED.format(kernel_name=kernel_name, minimum_version=MINIMUM_PIXI_VERSION)
        )

    # Ensure there is a Pixi project in the current working directory or any of its parents
    process, stdout, stderr = await subprocess_exec("pixi", "info", "--json", cwd=cwd, env=env)

    logger.info(f"pixi info stderr: {stderr}")
    logger.info(f"pixi info stdout: {stdout}")
    if process.returncode != 0:
        raise RuntimeError(f"Failed to run 'pixi info': {stderr}")

    try:
        pixi_info = PixiInfo.model_validate_json(stdout, strict=True)
    except ValidationError as exception:
        raise RuntimeError(
            f"Failed to parse 'pixi info' output: {stdout}\n{exception}"
        ) from exception

    if pixi_info.project is None:
        # Attempt to get a good error message by running `pixi project version get`. Maybe there's
        # a typo in the toml file (parsing error) or there is no project at all.
        process, stdout, stderr = await subprocess_exec(
            "pixi",
            "project",
            "version",
            "get",
            cwd=cwd,
            env=env,
        )
        raise RuntimeError(stderr)

    # Find the default environment and check if the required kernel package is a dependency
    for pixi_env in pixi_info.environments:
        if pixi_env.name == "default":
            default_environment = pixi_env
            break
    else:
        raise RuntimeError("Default Pixi environment not found.")

    dependencies = default_environment.dependencies + default_environment.pypi_dependencies
    if required_package not in dependencies:
        raise RuntimeError(
            PIXI_KERNEL_NOT_FOUND.format(
                kernel_name=kernel_name,
                required_package=required_package,
                prefix=default_environment.prefix,
            )
        )

    # Make sure the environment can be solved and is up-to-date
    process, stdout, stderr = await subprocess_exec("pixi", "install", cwd=cwd, env=env)
    if process.returncode != 0:
        raise RuntimeError(f"Failed to run 'pixi install': {stderr}")

    return default_environment
