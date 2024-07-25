import logging
import re
from pathlib import Path

import pytest

from pixi_kernel.errors import (
    PIXI_KERNEL_NOT_FOUND,
    PIXI_MANIFEST_NOT_FOUND,
    PIXI_NOT_FOUND,
    PIXI_VERSION_ERROR,
    PIXI_VERSION_NOT_SUPPORTED,
)
from pixi_kernel.pixi import (
    MINIMUM_PIXI_VERSION,
    PixiDiscoveryError,
    find_pixi_version,
    find_project_manifest,
)

data_dir = Path(__file__).parent / "data"
logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("_patch_path")
def test_pixi_not_installed():
    expected_error_message = re.escape(PIXI_NOT_FOUND.format(kernel_display_name="Pixi"))

    with pytest.raises(PixiDiscoveryError, match=expected_error_message):
        find_pixi_version(kernel_display_name="Pixi")


@pytest.mark.usefixtures("_patch_pixi_version_exit_code")
def test_pixi_version_bad_exit_code():
    expected_error_message = re.escape(PIXI_VERSION_ERROR.format(kernel_display_name="Pixi"))

    with pytest.raises(PixiDiscoveryError, match=expected_error_message):
        find_pixi_version(kernel_display_name="Pixi")


@pytest.mark.usefixtures("_patch_pixi_version_bad_stdout")
def test_pixi_version_bad_stdout():
    expected_error_message = re.escape(PIXI_VERSION_ERROR.format(kernel_display_name="Pixi"))

    with pytest.raises(PixiDiscoveryError, match=expected_error_message):
        find_pixi_version(kernel_display_name="Pixi")


@pytest.mark.usefixtures("_patch_pixi_version_value")
def test_outdated_pixi():
    expected_error_message = re.escape(
        PIXI_VERSION_NOT_SUPPORTED.format(
            kernel_display_name="Pixi",
            minimum_version=MINIMUM_PIXI_VERSION,
        )
    )

    with pytest.raises(PixiDiscoveryError, match=expected_error_message):
        find_pixi_version(kernel_display_name="Pixi")


def test_empty_project():
    cwd = Path("/")
    expected_error_message = re.escape(PIXI_MANIFEST_NOT_FOUND.format(cwd=cwd))

    find_pixi_version(kernel_display_name="Pixi")
    with pytest.raises(PixiDiscoveryError, match=expected_error_message):
        find_project_manifest(cwd=cwd, package_name="pixi", kernel_display_name="Pixi")


def test_missing_ipykernel():
    cwd = data_dir / "missing_ipykernel"
    package_name = "ipykernel"
    kernel_display_name = "Pixi - Python 3 (ipykernel)"

    expected_error_message = re.escape(
        PIXI_KERNEL_NOT_FOUND.format(
            package_name=package_name,
            kernel_display_name=kernel_display_name,
        )
    )

    find_pixi_version(kernel_display_name=kernel_display_name)
    with pytest.raises(PixiDiscoveryError, match=expected_error_message):
        find_project_manifest(
            cwd=cwd,
            package_name=package_name,
            kernel_display_name=kernel_display_name,
        )


def test_pixi_project():
    cwd = data_dir / "pixi_project"
    package_name = "ipykernel"
    kernel_display_name = "Pixi - Python 3 (ipykernel)"

    find_pixi_version(kernel_display_name=kernel_display_name)
    result = find_project_manifest(
        cwd=cwd,
        package_name=package_name,
        kernel_display_name=kernel_display_name,
    )
    assert result == (cwd / "pixi.toml").resolve()


def test_pyproject_project():
    cwd = data_dir / "pyproject_project"
    package_name = "ipykernel"
    kernel_display_name = "Pixi - Python 3 (ipykernel)"

    find_pixi_version(kernel_display_name=kernel_display_name)
    result = find_project_manifest(
        cwd=cwd,
        package_name=package_name,
        kernel_display_name=kernel_display_name,
    )
    assert result == (cwd / "pyproject.toml").resolve()
