import logging
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from pixi_kernel.errors import (
    PIXI_KERNEL_NOT_FOUND,
    PIXI_NOT_FOUND,
    PIXI_OUTDATED,
    PIXI_VERSION_ERROR,
)
from pixi_kernel.pixi import MINIMUM_PIXI_VERSION, ensure_readiness

data_dir = Path(__file__).parent / "data"
logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("_patch_path")
async def test_pixi_not_installed():
    message = re.escape(PIXI_NOT_FOUND.format(kernel_name="Pixi"))
    with pytest.raises(RuntimeError, match=message):
        await ensure_readiness(
            cwd=Path.cwd(), env=os.environ.copy(), required_package="pixi", kernel_name="Pixi"
        )


@pytest.mark.usefixtures("_patch_pixi_version_exit_code")
async def test_pixi_version_bad_exit_code():
    message = re.escape(PIXI_VERSION_ERROR.format(kernel_name="Pixi"))
    with pytest.raises(RuntimeError, match=message):
        await ensure_readiness(
            cwd=Path.cwd(), env=os.environ.copy(), required_package="pixi", kernel_name="Pixi"
        )


@pytest.mark.usefixtures("_patch_pixi_version_stdout")
async def test_pixi_version_bad_stdout():
    message = re.escape(PIXI_VERSION_ERROR.format(kernel_name="Pixi"))
    with pytest.raises(RuntimeError, match=message):
        await ensure_readiness(
            cwd=Path.cwd(), env=os.environ.copy(), required_package="pixi", kernel_name="Pixi"
        )


@pytest.mark.usefixtures("_patch_pixi_version")
async def test_outdated_pixi():
    message = re.escape(
        PIXI_OUTDATED.format(
            kernel_name="Pixi",
            minimum_version=MINIMUM_PIXI_VERSION,
        )
    )
    with pytest.raises(RuntimeError, match=message):
        await ensure_readiness(
            cwd=Path.cwd(), env=os.environ.copy(), required_package="pixi", kernel_name="Pixi"
        )


@pytest.mark.usefixtures("_patch_pixi_info_exit_code")
async def test_pixi_info_bad_exit_code():
    message = re.escape("Failed to run 'pixi info': error")
    with pytest.raises(RuntimeError, match=message):
        await ensure_readiness(
            cwd=Path.cwd(), env=os.environ.copy(), required_package="pixi", kernel_name="Pixi"
        )


@pytest.mark.usefixtures("_patch_pixi_info_stdout")
async def test_pixi_info_bad_stdout():
    message = re.escape(
        ("Failed to parse 'pixi info' output: not JSON\n1 validation error for PixiInfo")
    )
    with pytest.raises(RuntimeError, match=message):
        await ensure_readiness(
            cwd=Path.cwd(), env=os.environ.copy(), required_package="pixi", kernel_name="Pixi"
        )


async def test_empty_project():
    cwd = Path("/")
    assert not (cwd / "pixi.toml").exists(), "You should not have a pixi.toml file in /"
    assert not (cwd / "pyproject.toml").exists(), "You should not have a pyproject.toml file in /"

    message = re.escape(
        "could not find pixi.toml or pyproject.toml which is configured to use pixi"
    )
    with pytest.raises(RuntimeError, match=message):
        await ensure_readiness(
            cwd=cwd, env=os.environ.copy(), required_package="pixi", kernel_name="Pixi"
        )


async def test_bad_pixi_toml():
    cwd = data_dir / "bad_pixi_toml"
    message = re.escape("failed to parse project manifest") + "|" + re.escape("unknown field")
    with pytest.raises(RuntimeError, match=message):
        await ensure_readiness(
            cwd=cwd, env=os.environ.copy(), required_package="pixi", kernel_name="Pixi"
        )


@pytest.mark.usefixtures("_patch_pixi_info_no_default_env")
async def test_missing_default_environment():
    message = re.escape("Default Pixi environment not found.")
    with pytest.raises(RuntimeError, match=message):
        await ensure_readiness(
            cwd=Path.cwd(), env=os.environ.copy(), required_package="pixi", kernel_name="Pixi"
        )


async def test_missing_ipykernel():
    cwd = data_dir / "missing_ipykernel"
    required_package = "ipykernel"
    kernel_name = "Python (Pixi)"

    message = re.escape(
        PIXI_KERNEL_NOT_FOUND.format(
            required_package=required_package,
            kernel_name=kernel_name,
            prefix=str(cwd / ".pixi" / "envs" / "default"),
        )
    )
    with pytest.raises(RuntimeError, match=message):
        await ensure_readiness(
            cwd=cwd,
            env=os.environ.copy(),
            required_package=required_package,
            kernel_name=kernel_name,
        )


async def test_non_existing_dependency():
    cwd = data_dir / "non_existing_dependency"
    required_package = "ipykernel"
    kernel_name = "Python (Pixi)"

    message = re.escape("Failed to run 'pixi install':")
    with pytest.raises(RuntimeError, match=message):
        await ensure_readiness(
            cwd=cwd,
            env=os.environ.copy(),
            required_package=required_package,
            kernel_name=kernel_name,
        )


async def test_pixi_project():
    cwd = data_dir / "pixi_project"
    required_package = "ipykernel"
    kernel_name = "Python (Pixi)"

    environment = await ensure_readiness(
        cwd=cwd,
        env=os.environ.copy(),
        required_package=required_package,
        kernel_name=kernel_name,
    )
    assert Path(environment.prefix).parts[-2:] == ("envs", "default")


async def test_pyproject_project():
    cwd = data_dir / "pyproject_project"
    required_package = "ipykernel"
    kernel_name = "Python (Pixi)"

    environment = await ensure_readiness(
        cwd=cwd,
        env=os.environ.copy(),
        required_package=required_package,
        kernel_name=kernel_name,
    )
    assert Path(environment.prefix).parts[-2:] == ("envs", "default")


@pytest.fixture
def env_for_pixi_in_pixi():
    result = subprocess.run(
        ["pixi", "run", "printenv"],
        cwd=data_dir / "pixi_in_pixi",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    # Update the current environment where the tests are running to merge all the env vars returned
    # by `pixi run env`
    original_env = dict(os.environ)
    for line in result.stdout.splitlines():
        key, value = line.split("=", 1)
        os.environ[key] = value

    yield os.environ

    # Restore the original environment
    os.environ.clear()
    os.environ.update(original_env)


# https://github.com/renan-r-santos/pixi-kernel/issues/35
@pytest.mark.skipif(sys.platform == "win32", reason="No need to write Windows-specific code here")
async def test_pixi_in_pixi(env_for_pixi_in_pixi: dict[str, str]):
    cwd = data_dir / "pixi_in_pixi" / "good_project"
    required_package = "ipykernel"
    kernel_name = "Python (Pixi)"

    environment = await ensure_readiness(
        cwd=cwd,
        env=env_for_pixi_in_pixi,
        required_package=required_package,
        kernel_name=kernel_name,
    )
    assert Path(environment.prefix).parts[-2:] == ("envs", "default")
