import json
from dataclasses import dataclass

import pytest

import pixi_kernel.pixi


@dataclass
class MockProcessResult:
    returncode: int


@pytest.fixture
def _patch_path(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("PATH", raising=False)


@pytest.fixture
def _patch_pixi_version_exit_code(monkeypatch: pytest.MonkeyPatch):
    orig_subprocess_exec = pixi_kernel.pixi.subprocess_exec

    async def mock_subprocess_exec(cmd, *args, **kwargs):
        if cmd == "pixi" and args == ("--version",):
            return MockProcessResult(1), "", ""
        else:
            return await orig_subprocess_exec(cmd, *args, **kwargs)

    monkeypatch.setattr("pixi_kernel.pixi.subprocess_exec", mock_subprocess_exec)


@pytest.fixture
def _patch_pixi_version_stdout(monkeypatch: pytest.MonkeyPatch):
    orig_subprocess_exec = pixi_kernel.pixi.subprocess_exec

    async def mock_subprocess_exec(cmd, *args, **kwargs):
        if cmd == "pixi" and args == ("--version",):
            return MockProcessResult(0), "wrong output", ""
        else:
            return await orig_subprocess_exec(cmd, *args, **kwargs)

    monkeypatch.setattr("pixi_kernel.pixi.subprocess_exec", mock_subprocess_exec)


@pytest.fixture
def _patch_pixi_version(monkeypatch: pytest.MonkeyPatch):
    orig_subprocess_exec = pixi_kernel.pixi.subprocess_exec

    async def mock_subprocess_exec(cmd, *args, **kwargs):
        if cmd == "pixi" and args == ("--version",):
            process, stdout, stderr = await orig_subprocess_exec(cmd, *args, **kwargs)
            assert process.returncode == 0
            assert stdout.startswith("pixi ")

            stdout = "pixi 0.15.0\n"
            return process, stdout, stderr
        else:
            return await orig_subprocess_exec(cmd, *args, **kwargs)

    monkeypatch.setattr("pixi_kernel.pixi.subprocess_exec", mock_subprocess_exec)


@pytest.fixture
def _patch_pixi_info_exit_code(monkeypatch: pytest.MonkeyPatch):
    orig_subprocess_exec = pixi_kernel.pixi.subprocess_exec

    async def mock_subprocess_exec(cmd, *args, **kwargs):
        if cmd == "pixi" and args == ("info", "--json"):
            return MockProcessResult(1), "", "error"
        else:
            return await orig_subprocess_exec(cmd, *args, **kwargs)

    monkeypatch.setattr("pixi_kernel.pixi.subprocess_exec", mock_subprocess_exec)


@pytest.fixture
def _patch_pixi_info_stdout(monkeypatch: pytest.MonkeyPatch):
    orig_subprocess_exec = pixi_kernel.pixi.subprocess_exec

    async def mock_subprocess_exec(cmd, *args, **kwargs):
        if cmd == "pixi" and args == ("info", "--json"):
            return MockProcessResult(0), "not JSON", ""
        else:
            return await orig_subprocess_exec(cmd, *args, **kwargs)

    monkeypatch.setattr("pixi_kernel.pixi.subprocess_exec", mock_subprocess_exec)


@pytest.fixture
def _patch_pixi_info_no_default_env(monkeypatch: pytest.MonkeyPatch):
    orig_subprocess_exec = pixi_kernel.pixi.subprocess_exec

    async def mock_subprocess_exec(cmd, *args, **kwargs):
        if cmd == "pixi" and args == ("info", "--json"):
            return (
                MockProcessResult(0),
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

    monkeypatch.setattr("pixi_kernel.pixi.subprocess_exec", mock_subprocess_exec)
