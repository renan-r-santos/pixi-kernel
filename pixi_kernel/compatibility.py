import shutil
import sys
from pathlib import Path
from typing import Any

from returns.result import Failure, Result, Success

from .async_subprocess import subprocess_exec

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


MINIMUM_PIXI_VERSION = (0, 39, 0)


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


# Cache for the Pixi path
_pixi_path_cache: str | None = None


def get_config_file() -> Path:
    return Path.home() / ".config" / "pixi-kernel" / "config.toml"


def get_default_pixi_path() -> Path:
    if sys.platform == "win32":
        return Path.home() / ".pixi" / "bin" / "pixi.exe"
    else:
        return Path.home() / ".pixi" / "bin" / "pixi"


def find_pixi_binary() -> Result[str, None]:
    # Return cached result if available
    if _pixi_path_cache is not None:
        return Success(_pixi_path_cache)

    # 1. Check if the Pixi binary is available in the system PATH
    pixi_path = shutil.which("pixi")
    if pixi_path is not None:
        return Success(pixi_path)

    # 2. Check if a config file exists and read the Pixi path from it
    config_file = get_config_file()
    if config_file.is_file():
        try:
            content = Path(config_file).read_text()
            config = tomllib.loads(content)
            pixi_path = config.get("pixi-path")
            if pixi_path is not None and Path(pixi_path).is_file():
                return Success(pixi_path)
        except (OSError, tomllib.TOMLDecodeError):
            pass

    # 3. Check if the default installation path exists
    # https://pixi.sh/latest/installation/#installer-script-options
    default_pixi_path = get_default_pixi_path()
    if default_pixi_path.is_file():
        return Success(str(default_pixi_path))

    return Failure(None)


async def has_compatible_pixi() -> Result[None, str]:
    global _pixi_path_cache

    if _pixi_path_cache is not None:
        return Success(None)

    result = find_pixi_binary()

    if isinstance(result, Failure):
        return Failure(PIXI_NOT_FOUND)
    else:
        pixi_path = result.unwrap()

    returncode, stdout, _ = await subprocess_exec(pixi_path, "--version")
    if returncode != 0 or not stdout.startswith("pixi "):
        return Failure(PIXI_VERSION_ERROR)

    pixi_version = stdout[len("pixi ") :].strip()
    major, minor, patch = map(int, pixi_version.split("."))

    if (major, minor, patch) < MINIMUM_PIXI_VERSION:
        minimum_version = ".".join(map(str, MINIMUM_PIXI_VERSION))
        return Failure(PIXI_OUTDATED.format(minimum_version=minimum_version))

    # We found a compatible Pixi binary, cache it
    _pixi_path_cache = pixi_path
    return Success(None)


async def run_pixi(*args: str, **kwargs: Any) -> tuple[int, str, str]:
    # It is safe to unwrap as `has_compatible_pixi()` would already have checked for a compatible
    # Pixi binary.
    pixi = find_pixi_binary().unwrap()

    return await subprocess_exec(pixi, *args, **kwargs)
