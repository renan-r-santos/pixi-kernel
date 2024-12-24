import shutil

from returns.result import Failure, Result, Success

from .async_subprocess import subprocess_exec

MINIMUM_PIXI_VERSION = (0, 30, 0)


PIXI_NOT_FOUND = """Pixi was not detected in your system.
Please, follow the steps below to install Pixi:
    1. Visit the Pixi installation guide at https://pixi.sh/.
    2. Verify Pixi was installed by running 'which pixi' in your terminal.
    3. Restart JupyterLab.

If you continue to face issues, report them at https://github.com/renan-r-santos/pixi-kernel/issues
"""

PIXI_VERSION_ERROR = """Pixi was detected in your system but it appears to be corrupted.
Please, follow the steps below to reinstall Pixi:
    1. Visit the Pixi installation guide at https://pixi.sh/.
    3. Verify that Pixi is working by running 'pixi --version' in your terminal.
    3. Restart JupyterLab.

If you continue to face issues, report them at https://github.com/renan-r-santos/pixi-kernel/issues
"""

PIXI_OUTDATED = """Pixi was detected in your system but it appears to be outdated.
You need at least Pixi v{minimum_version} in order to run Pixi kernels.
Open a terminal and run 'pixi self-update' to update Pixi to its latest version
and then restart JupyterLab.

If you continue to face issues, report them at https://github.com/renan-r-santos/pixi-kernel/issues
"""


async def has_compatible_pixi() -> Result[None, str]:
    if shutil.which("pixi") is None:
        return Failure(PIXI_NOT_FOUND)

    returncode, stdout, stderr = await subprocess_exec("pixi", "--version")
    if returncode != 0 or not stdout.startswith("pixi "):
        return Failure(PIXI_VERSION_ERROR)

    pixi_version = stdout[len("pixi ") :].strip()
    major, minor, patch = map(int, pixi_version.split("."))

    if (major, minor, patch) < MINIMUM_PIXI_VERSION:
        minimum_version = ".".join(map(str, MINIMUM_PIXI_VERSION))
        return Failure(PIXI_OUTDATED.format(minimum_version=minimum_version))

    return Success(None)
