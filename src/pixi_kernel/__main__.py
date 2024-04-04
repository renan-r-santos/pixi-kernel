import logging
import shutil
import subprocess
from pathlib import Path
from typing import Union

import msgspec
from packaging import version

from .exceptions import PixiKernelError
from .kernels import start_fallback_kernel, start_pixi_kernel
from .pixi import PixiInfo

MINIMUM_PIXI_VERSION = "0.18.0"

logger = logging.getLogger(__name__)


def find_project_manifest() -> Union[str, PixiKernelError]:
    # Ensure pixi is installed
    if shutil.which("pixi") is None:
        return PixiKernelError(
            message=(
                "Pixi is not installed. "
                "Follow the installation guide at https://pixi.sh/latest/ to install it."
            )
        )

    # Ensure a supported pixi version is installed
    result = subprocess.run(["pixi", "--version"], capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.startswith("pixi "):
        message = (
            "Failed to get pixi version. Make sure pixi is installed or follow the "
            "installation guide at https://pixi.sh/latest/ to install it.\n"
            f"Return code: {result.returncode}\n"
            f"Output: {result.stdout}\n"
            f"Error: {result.stderr}"
        )
        return PixiKernelError(message=message)

    pixi_version = result.stdout[len("pixi ") :].strip()
    if version.parse(pixi_version) < version.parse(MINIMUM_PIXI_VERSION):
        return PixiKernelError(
            message=(
                f"Pixi version {pixi_version} not supported. "
                f"Please upgrade to version {MINIMUM_PIXI_VERSION} or later."
            )
        )
    logger.info(f"Found pixi {pixi_version}")

    # Find project's manifest file
    cwd = Path.cwd().resolve()
    candidate_dirs = [cwd, *cwd.parents]
    for dir in candidate_dirs:
        result = subprocess.run(["pixi", "info", "--json"], cwd=dir, capture_output=True)
        if result.returncode != 0:
            logger.error(f"Failed to get pixi info for directory {dir}: {result.stderr}")
            continue

        try:
            pixi_info = msgspec.json.decode(result.stdout, type=PixiInfo)
        except msgspec.ValidationError as exception:
            logger.error(f"Failed to parse pixi info {result.stdout}: {exception}")
            continue

        if len(pixi_info.environments_info) == 0:
            continue

        for env in pixi_info.environments_info:
            if env.name == "default" and pixi_info.project_info is not None:
                if "ipykernel" not in env.dependencies + env.pypi_dependencies:
                    return PixiKernelError(
                        message=(
                            f"The project at {dir} does not have ipykernel as a dependency in the "
                            "default environment. Please add it by running `pixi add ipykernel` "
                            "and restart your kernel."
                        )
                    )
                return pixi_info.project_info.manifest_path

    return PixiKernelError(
        message=("Pixi project not found. Run `pixi init` in the project directory.")
    )


def main():
    logging.basicConfig(level=logging.INFO, format="pixi-kernel: %(message)s")

    maybe_manifest_path = find_project_manifest()
    if isinstance(maybe_manifest_path, PixiKernelError):
        start_fallback_kernel(maybe_manifest_path.message)
    else:
        start_pixi_kernel(maybe_manifest_path)


if __name__ == "__main__":
    main()
