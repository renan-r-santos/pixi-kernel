import logging
from pathlib import Path

from pydantic import ValidationError
from returns.result import Failure, Result, Success

from .async_subprocess import subprocess_exec
from .compatibility import has_compatible_pixi
from .types import Environment, PixiInfo

logger = logging.getLogger(__name__)

PIXI_KERNEL_NOT_FOUND = """To run the {kernel_name} kernel, you need to add the {required_package}
package to your project dependencies and restart your kernel. The project environment prefix is
{prefix}.
Make sure this path points to the correct environment.

If you continue to face issues, report them at https://github.com/renan-r-santos/pixi-kernel/issues
"""


async def verify_env_readiness(
    *,
    environment_name: str,
    cwd: Path,
    env: dict[str, str],
    required_package: str,
    kernel_name: str,
) -> Result[Environment, str]:
    """Ensure the Pixi environment is ready to run the kernel.

    If any of the checks fail, a Failure is returned and Pixi Kernel will launch a fallback kernel
    that will display the error message to the user.
    """
    # Remove PIXI_IN_SHELL for when JupyterLab is started from a Pixi shell
    # https://github.com/renan-r-santos/pixi-kernel/issues/35
    env.pop("PIXI_IN_SHELL", None)

    result = await has_compatible_pixi()
    if isinstance(result, Failure):
        return result

    # Ensure there is a Pixi project in the current working directory or any of its parents
    returncode, stdout, stderr = await subprocess_exec("pixi", "info", "--json", cwd=cwd, env=env)

    logger.info(f"pixi info stderr: {stderr}")
    logger.info(f"pixi info stdout: {stdout}")
    if returncode != 0:
        return Failure(f"Failed to run 'pixi info': {stderr}")

    try:
        pixi_info = PixiInfo.model_validate_json(stdout, strict=True)
    except ValidationError as exception:
        return Failure(f"Failed to parse 'pixi info' output: {stdout}\n{exception}")

    if pixi_info.project is None:
        # Attempt to get a good error message by running `pixi project version get`. Maybe there's
        # a typo in the toml file (parsing error) or there is no project at all.
        returncode, stdout, stderr = await subprocess_exec(
            "pixi",
            "project",
            "version",
            "get",
            cwd=cwd,
            env=env,
        )
        return Failure(stderr)

    # Find the Pixi environment and check if the required kernel package is a dependency
    for pixi_env in pixi_info.environments:
        if pixi_env.name == environment_name:
            pixi_environment = pixi_env
            break
    else:
        return Failure(f"Pixi environment {environment_name} not found.")

    dependencies = pixi_environment.dependencies + pixi_environment.pypi_dependencies
    if required_package not in dependencies:
        return Failure(
            PIXI_KERNEL_NOT_FOUND.format(
                kernel_name=kernel_name,
                required_package=required_package,
                prefix=pixi_environment.prefix,
            )
        )

    # Make sure the environment can be solved and is up-to-date
    returncode, stdout, stderr = await subprocess_exec(
        "pixi",
        "install",
        "--environment",
        environment_name,
        cwd=cwd,
        env=env,
    )
    if returncode != 0:
        return Failure(f"Failed to run 'pixi install --environment {environment_name}': {stderr}")

    return Success(pixi_environment)
