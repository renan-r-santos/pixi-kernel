from pathlib import Path

import pytest

from pixi_kernel.__main__ import find_project_manifest
from pixi_kernel.exceptions import PixiKernelError

data_dir = Path(__file__).parent / "data"


@pytest.mark.usefixtures("_patch_path")
def test_pixi_not_installed():
    result = find_project_manifest()
    assert isinstance(result, PixiKernelError)
    assert "Pixi is not installed" in result.message


@pytest.mark.usefixtures("_patch_subprocess_exit_code")
def test_pixi_version_fail():
    result = find_project_manifest()
    assert isinstance(result, PixiKernelError)
    assert "Failed to get pixi version" in result.message


@pytest.mark.usefixtures("_patch_subprocess_stdout")
def test_pixi_version_wrong_stdout():
    result = find_project_manifest()
    assert isinstance(result, PixiKernelError)
    assert "Failed to get pixi version" in result.message


@pytest.mark.usefixtures("_patch_pixi_version")
def test_unsupported_pixi_version():
    result = find_project_manifest()
    assert isinstance(result, PixiKernelError)
    assert "Please upgrade to version" in result.message


def test_empty_project(cwd):
    with cwd(data_dir / "empty_project"):
        result = find_project_manifest()
        assert isinstance(result, PixiKernelError)
        assert "Pixi project not found" in result.message


def test_missing_ipykernel(cwd):
    with cwd(data_dir / "missing_ipykernel"):
        result = find_project_manifest()
        assert isinstance(result, PixiKernelError)
        assert "does not have ipykernel as a dependency" in result.message


def test_pixi_project(cwd):
    with cwd(data_dir / "pixi_project"):
        result = find_project_manifest()
        assert result == str((data_dir / "pixi_project" / "pixi.toml").resolve())


def test_pyproject_project(cwd):
    with cwd(data_dir / "pyproject_project"):
        result = find_project_manifest()
        assert result == str((data_dir / "pyproject_project" / "pyproject.toml").resolve())
