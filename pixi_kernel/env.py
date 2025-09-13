import os
from pathlib import Path

import msgspec

from .compatibility import run_pixi
from .types import PixiInfo

DEFAULT_ENVIRONMENT = "default"


async def envs_from_path(path: Path) -> list[str]:
    # Remove PIXI_IN_SHELL for when JupyterLab is started from a Pixi shell
    # https://github.com/renan-r-santos/pixi-kernel/issues/35
    env = os.environ.copy()
    env.pop("PIXI_IN_SHELL", None)

    returncode, stdout, _ = await run_pixi("info", "--json", cwd=path, env=env)
    if returncode != 0:
        return [DEFAULT_ENVIRONMENT]

    try:
        pixi_info = msgspec.json.decode(stdout, type=PixiInfo)
    except msgspec.MsgspecError:
        return [DEFAULT_ENVIRONMENT]

    if len(pixi_info.environments) == 0:
        return [DEFAULT_ENVIRONMENT]

    return sorted([env.name for env in pixi_info.environments])
