import asyncio
import json
import platform

import pixi_kernel.compatibility
import pixi_kernel.readiness
import pytest

if platform.system() == "Windows":
    # Test both event loop policies on Windows
    # https://github.com/renan-r-santos/pixi-kernel/issues/39
    @pytest.fixture(
        scope="session",
        params=(
            asyncio.WindowsSelectorEventLoopPolicy(),
            asyncio.WindowsProactorEventLoopPolicy(),
        ),
    )
    def event_loop_policy(request: pytest.FixtureRequest):
        return request.param


@pytest.fixture
def _patch_path(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("PATH", raising=False)


@pytest.fixture
def _patch_pixi_version_exit_code(monkeypatch: pytest.MonkeyPatch):
    orig_subprocess_exec = pixi_kernel.compatibility.subprocess_exec

    async def mock_subprocess_exec(cmd, *args, **kwargs):
        if cmd == "pixi" and args == ("--version",):
            return 1, "", ""
        else:
            return await orig_subprocess_exec(cmd, *args, **kwargs)

    monkeypatch.setattr(pixi_kernel.compatibility, "subprocess_exec", mock_subprocess_exec)


@pytest.fixture
def _patch_pixi_version_stdout(monkeypatch: pytest.MonkeyPatch):
    orig_subprocess_exec = pixi_kernel.compatibility.subprocess_exec

    async def mock_subprocess_exec(cmd, *args, **kwargs):
        if cmd == "pixi" and args == ("--version",):
            return 0, "wrong output", ""
        else:
            return await orig_subprocess_exec(cmd, *args, **kwargs)

    monkeypatch.setattr(pixi_kernel.compatibility, "subprocess_exec", mock_subprocess_exec)


@pytest.fixture
def _patch_pixi_version(monkeypatch: pytest.MonkeyPatch):
    orig_subprocess_exec = pixi_kernel.compatibility.subprocess_exec

    async def mock_subprocess_exec(cmd, *args, **kwargs):
        if cmd == "pixi" and args == ("--version",):
            returncode, stdout, stderr = await orig_subprocess_exec(cmd, *args, **kwargs)
            assert returncode == 0
            assert stdout.startswith("pixi ")

            stdout = "pixi 0.15.0\n"
            return returncode, stdout, stderr
        else:
            return await orig_subprocess_exec(cmd, *args, **kwargs)

    monkeypatch.setattr(pixi_kernel.compatibility, "subprocess_exec", mock_subprocess_exec)


@pytest.fixture
def _patch_pixi_info_exit_code(monkeypatch: pytest.MonkeyPatch):
    orig_subprocess_exec = pixi_kernel.readiness.subprocess_exec

    async def mock_subprocess_exec(cmd, *args, **kwargs):
        if cmd == "pixi" and args == ("info", "--json"):
            return 1, "", "error"
        else:
            return await orig_subprocess_exec(cmd, *args, **kwargs)

    monkeypatch.setattr(pixi_kernel.readiness, "subprocess_exec", mock_subprocess_exec)


@pytest.fixture
def _patch_pixi_info_stdout(monkeypatch: pytest.MonkeyPatch):
    orig_subprocess_exec = pixi_kernel.readiness.subprocess_exec

    async def mock_subprocess_exec(cmd, *args, **kwargs):
        if cmd == "pixi" and args == ("info", "--json"):
            return 0, "not JSON", ""
        else:
            return await orig_subprocess_exec(cmd, *args, **kwargs)

    monkeypatch.setattr(pixi_kernel.readiness, "subprocess_exec", mock_subprocess_exec)


@pytest.fixture
def _patch_pixi_info_no_default_env(monkeypatch: pytest.MonkeyPatch):
    orig_subprocess_exec = pixi_kernel.readiness.subprocess_exec

    async def mock_subprocess_exec(cmd, *args, **kwargs):
        if cmd == "pixi" and args == ("info", "--json"):
            return (
                0,
                json.dumps(
                    {
                        "project_info": {"manifest_path": "/"},
                        "environments_info": [
                            {
                                "name": "test",
                                "dependencies": [],
                                "pypi_dependencies": [],
                                "prefix": "",
                            },
                        ],
                    }
                ),
                "",
            )
        else:
            return await orig_subprocess_exec(cmd, *args, **kwargs)

    monkeypatch.setattr(pixi_kernel.readiness, "subprocess_exec", mock_subprocess_exec)
