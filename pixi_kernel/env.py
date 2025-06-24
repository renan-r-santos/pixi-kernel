import os
from pathlib import Path

from pydantic import ValidationError

from .async_subprocess import subprocess_exec
from .types import PixiInfo

DEFAULT_ENVIRONMENT = "default"


async def envs_from_path(path: Path) -> list[str]:
    # Remove PIXI_IN_SHELL for when JupyterLab is started from a Pixi shell
    # https://github.com/renan-r-santos/pixi-kernel/issues/35
    env = os.environ.copy()
    env.pop("PIXI_IN_SHELL", None)

    returncode, stdout, stderr = await subprocess_exec("pixi", "info", "--json", cwd=path, env=env)
    if returncode != 0:
        return [DEFAULT_ENVIRONMENT]

    try:
        pixi_info = PixiInfo.model_validate_json(stdout, strict=True)
    except ValidationError:
        return [DEFAULT_ENVIRONMENT]

    if len(pixi_info.environments) == 0:
        return [DEFAULT_ENVIRONMENT]

    return [env.name for env in pixi_info.environments]
