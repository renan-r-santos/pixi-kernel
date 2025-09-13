import logging
import os
import subprocess
import sys
from pathlib import Path

import pytest
from pixi_kernel.compatibility import (
    MINIMUM_PIXI_VERSION,
    PIXI_NOT_FOUND,
    PIXI_OUTDATED,
    PIXI_VERSION_ERROR,
)
from pixi_kernel.readiness import PIXI_KERNEL_NOT_FOUND, verify_env_readiness

data_dir = Path(__file__).parent / "data"


@pytest.fixture
def kwargs():
    return {
        "environment_name": "default",
        "cwd": Path.cwd(),
        "env": os.environ.copy(),
        "required_package": "ipykernel",
        "kernel_name": "Pixi",
        "logger": logging.getLogger("pixi_kernel"),
    }


@pytest.mark.usefixtures("_patch_find_pixi_binary")
async def test_pixi_not_installed(kwargs: dict):
    expected = PIXI_NOT_FOUND.format(kernel_name=kwargs["kernel_name"])
    result = await verify_env_readiness(**kwargs)
    assert result.failure() == expected


@pytest.mark.usefixtures("_patch_pixi_version_exit_code")
async def test_pixi_version_bad_exit_code(kwargs: dict):
    expected = PIXI_VERSION_ERROR.format(kernel_name=kwargs["kernel_name"])
    result = await verify_env_readiness(**kwargs)
    assert result.failure() == expected


@pytest.mark.usefixtures("_patch_pixi_version_stdout")
async def test_pixi_version_bad_stdout(kwargs: dict):
    expected = PIXI_VERSION_ERROR.format(kernel_name=kwargs["kernel_name"])
    result = await verify_env_readiness(**kwargs)
    assert result.failure() == expected


@pytest.mark.usefixtures("_patch_pixi_version")
async def test_outdated_pixi(kwargs: dict):
    minimum_version = ".".join(map(str, MINIMUM_PIXI_VERSION))
    expected = PIXI_OUTDATED.format(
        kernel_name=kwargs["kernel_name"],
        minimum_version=minimum_version,
    )
    result = await verify_env_readiness(**kwargs)
    assert result.failure() == expected


@pytest.mark.usefixtures("_patch_pixi_info_exit_code")
async def test_pixi_info_bad_exit_code(kwargs: dict):
    result = await verify_env_readiness(**kwargs)
    assert result.failure().startswith("Failed to run 'pixi info'")


@pytest.mark.usefixtures("_patch_pixi_info_stdout")
async def test_pixi_info_bad_stdout(kwargs: dict):
    result = await verify_env_readiness(**kwargs)
    assert result.failure().startswith("Failed to parse 'pixi info' output")


async def test_empty_project(kwargs: dict):
    kwargs["cwd"] = cwd = Path("/")
    assert not (cwd / "pixi.toml").exists(), "You should not have a pixi.toml file in /"
    assert not (cwd / "pyproject.toml").exists(), "You should not have a pyproject.toml file in /"

    result = await verify_env_readiness(**kwargs)
    assert "could not find pixi.toml or pyproject.toml" in result.failure()


async def test_bad_pixi_toml(kwargs: dict):
    kwargs["cwd"] = data_dir / "bad_pixi_toml"
    result = await verify_env_readiness(**kwargs)
    assert "unknown field" in result.failure() or "Unexpected keys" in result.failure()


@pytest.mark.usefixtures("_patch_pixi_info_no_default_env")
async def test_missing_default_environment(kwargs: dict):
    result = await verify_env_readiness(**kwargs)
    assert result.failure() == f"Pixi environment {kwargs['environment_name']} not found."


async def test_missing_ipykernel(kwargs: dict):
    kwargs["cwd"] = cwd = data_dir / "missing_ipykernel"
    expected = PIXI_KERNEL_NOT_FOUND.format(
        required_package=kwargs["required_package"],
        kernel_name=kwargs["kernel_name"],
        prefix=str(cwd / ".pixi" / "envs" / "default"),
    )
    result = await verify_env_readiness(**kwargs)
    assert result.failure() == expected


async def test_non_existing_dependency(kwargs: dict):
    kwargs["cwd"] = data_dir / "non_existing_dependency"
    result = await verify_env_readiness(**kwargs)
    assert result.failure().startswith(
        f"Failed to run 'pixi install --environment {kwargs['environment_name']}'"
    )


async def test_pixi_project(kwargs: dict):
    kwargs["cwd"] = data_dir / "pixi_project"
    result = await verify_env_readiness(**kwargs)
    environment = result.unwrap()
    assert Path(environment.prefix).parts[-2:] == ("envs", "default")


async def test_pyproject_project(kwargs: dict):
    kwargs["cwd"] = data_dir / "pyproject_project"
    result = await verify_env_readiness(**kwargs)
    environment = result.unwrap()
    assert Path(environment.prefix).parts[-2:] == ("envs", "default")


async def test_transitive_dependency(kwargs: dict):
    kwargs["environment_name"] = "test"
    kwargs["cwd"] = data_dir / "transitive_dependency"
    result = await verify_env_readiness(**kwargs)
    environment = result.unwrap()
    assert Path(environment.prefix).parts[-2:] == ("envs", "test")


@pytest.fixture
def env_for_pixi_in_pixi():
    cwd = data_dir / "pixi_in_pixi"
    process = subprocess.run(["pixi", "run", "printenv"], cwd=cwd, capture_output=True, text=True)
    assert process.returncode == 0, process.stderr
    return dict(line.split("=", 1) for line in process.stdout.splitlines())


# https://github.com/renan-r-santos/pixi-kernel/issues/35
@pytest.mark.skipif(sys.platform == "win32", reason="No need to write Windows-specific code here")
async def test_pixi_in_pixi(kwargs: dict, env_for_pixi_in_pixi: dict[str, str]):
    kwargs["cwd"] = data_dir / "pixi_in_pixi" / "good_project"
    kwargs["env"] = env_for_pixi_in_pixi
    assert "PIXI_IN_SHELL" in kwargs["env"]

    result = await verify_env_readiness(**kwargs)
    environment = result.unwrap()
    assert Path(environment.prefix).parts[-2:] == ("envs", "default")
