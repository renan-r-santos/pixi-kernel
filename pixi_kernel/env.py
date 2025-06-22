import os
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from .async_subprocess import subprocess_exec
from .types import PixiInfo


@dataclass(frozen=True)
class PixiEnvironment:
    name: str
    default: bool = False


DEFAULT_ENVIRONMENT = PixiEnvironment(name="default", default=True)


async def envs_from_path(path: Path) -> list[PixiEnvironment]:
    # Remove PIXI_IN_SHELL for when JupyterLab is started from a Pixi shell
    # https://github.com/renan-r-santos/pixi-kernel/issues/35
    env = os.environ.copy()
    env.pop("PIXI_IN_SHELL", None)

    default_env_name = os.environ.get("PIXI_KERNEL_DEFAULT_ENVIRONMENT", DEFAULT_ENVIRONMENT.name)

    returncode, stdout, stderr = await subprocess_exec("pixi", "info", "--json", cwd=path, env=env)
    if returncode != 0:
        return [DEFAULT_ENVIRONMENT]

    try:
        pixi_info = PixiInfo.model_validate_json(stdout, strict=True)
    except ValidationError:
        return [DEFAULT_ENVIRONMENT]

    if len(pixi_info.environments) == 0:
        return [DEFAULT_ENVIRONMENT]

    envs: list[PixiEnvironment] = []
    found_default = False
    for env_obj in pixi_info.environments:
        is_default = env_obj.name == default_env_name
        if is_default:
            found_default = True
        envs.append(PixiEnvironment(name=env_obj.name, default=is_default))

    # If no environment matched the default, fallback to "default" if present
    if not found_default:
        for env in envs:
            if env.name == DEFAULT_ENVIRONMENT.name:
                env.default = True
                found_default = True
                break

    # If an environment named "default" is not present (is this even possible?), just set the first
    # as default
    if not found_default and envs:
        envs[0].default = True

    return envs
