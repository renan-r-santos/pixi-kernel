import logging
import re
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
def test_pixi_not_installed():
    message = re.escape(PIXI_NOT_FOUND.format(kernel_name="Pixi"))
    with pytest.raises(RuntimeError, match=message):
        ensure_readiness(cwd=Path.cwd(), required_package="pixi", kernel_name="Pixi")


@pytest.mark.usefixtures("_patch_pixi_version_exit_code")
def test_pixi_version_bad_exit_code():
    message = re.escape(PIXI_VERSION_ERROR.format(kernel_name="Pixi"))
    with pytest.raises(RuntimeError, match=message):
        ensure_readiness(cwd=Path.cwd(), required_package="pixi", kernel_name="Pixi")


@pytest.mark.usefixtures("_patch_pixi_version_stdout")
def test_pixi_version_bad_stdout():
    message = re.escape(PIXI_VERSION_ERROR.format(kernel_name="Pixi"))
    with pytest.raises(RuntimeError, match=message):
        ensure_readiness(cwd=Path.cwd(), required_package="pixi", kernel_name="Pixi")


@pytest.mark.usefixtures("_patch_pixi_version")
def test_outdated_pixi():
    message = re.escape(
        PIXI_OUTDATED.format(
            kernel_name="Pixi",
            minimum_version=MINIMUM_PIXI_VERSION,
        )
    )
    with pytest.raises(RuntimeError, match=message):
        ensure_readiness(cwd=Path.cwd(), required_package="pixi", kernel_name="Pixi")


@pytest.mark.usefixtures("_patch_pixi_info_exit_code")
def test_pixi_info_bad_exit_code():
    message = re.escape("Failed to run 'pixi info': error")
    with pytest.raises(RuntimeError, match=message):
        ensure_readiness(cwd=Path.cwd(), required_package="pixi", kernel_name="Pixi")


@pytest.mark.usefixtures("_patch_pixi_info_stdout")
def test_pixi_info_bad_stdout():
    message = re.escape(
        ("Failed to parse 'pixi info' output: not JSON\n1 validation error for PixiInfo")
    )
    with pytest.raises(RuntimeError, match=message):
        ensure_readiness(cwd=Path.cwd(), required_package="pixi", kernel_name="Pixi")


def test_empty_project():
    cwd = Path("/")
    assert not (cwd / "pixi.toml").exists(), "You should not have a pixi.toml file in /"
    assert not (cwd / "pyproject.toml").exists(), "You should not have a pyproject.toml file in /"

    message = re.escape(
        "could not find pixi.toml or pyproject.toml which is configured to use pixi"
    )
    with pytest.raises(RuntimeError, match=message):
        ensure_readiness(cwd=cwd, required_package="pixi", kernel_name="Pixi")


def test_bad_pixi_toml():
    cwd = data_dir / "bad_pixi_toml"
    message = re.escape("failed to parse project manifest")
    with pytest.raises(RuntimeError, match=message):
        ensure_readiness(cwd=cwd, required_package="pixi", kernel_name="Pixi")


@pytest.mark.usefixtures("_patch_pixi_info_no_default_env")
def test_missing_default_environment():
    message = re.escape("Default Pixi environment not found.")
    with pytest.raises(RuntimeError, match=message):
        ensure_readiness(cwd=Path.cwd(), required_package="pixi", kernel_name="Pixi")


def test_missing_ipykernel():
    cwd = data_dir / "missing_ipykernel"
    required_package = "ipykernel"
    kernel_name = "Python (Pixi)"

    message = re.escape(
        PIXI_KERNEL_NOT_FOUND.format(
            required_package=required_package,
            kernel_name=kernel_name,
        )
    )
    with pytest.raises(RuntimeError, match=message):
        ensure_readiness(cwd=cwd, required_package=required_package, kernel_name=kernel_name)


def test_non_existing_dependency():
    cwd = data_dir / "non_existing_dependency"
    required_package = "ipykernel"
    kernel_name = "Python (Pixi)"

    message = re.escape("Failed to run 'pixi install':")
    with pytest.raises(RuntimeError, match=message):
        ensure_readiness(cwd=cwd, required_package=required_package, kernel_name=kernel_name)


def test_pixi_project():
    cwd = data_dir / "pixi_project"
    required_package = "ipykernel"
    kernel_name = "Python (Pixi)"

    environment = ensure_readiness(
        cwd=cwd,
        required_package=required_package,
        kernel_name=kernel_name,
    )
    assert Path(environment.prefix).parts[-2:] == ("envs", "default")


def test_pyproject_project():
    cwd = data_dir / "pyproject_project"
    required_package = "ipykernel"
    kernel_name = "Python (Pixi)"

    environment = ensure_readiness(
        cwd=cwd,
        required_package=required_package,
        kernel_name=kernel_name,
    )
    assert Path(environment.prefix).parts[-2:] == ("envs", "default")
