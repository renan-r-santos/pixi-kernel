import json
import subprocess

import pytest


@pytest.fixture
def _patch_path(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("PATH", raising=False)


@pytest.fixture
def _patch_pixi_version_exit_code(monkeypatch: pytest.MonkeyPatch):
    original_run = subprocess.run

    def mock_run(cmd, *args, **kwargs):
        if cmd == ["pixi", "--version"]:
            return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr="")
        else:
            return original_run(cmd, *args, **kwargs)

    monkeypatch.setattr("subprocess.run", mock_run)


@pytest.fixture
def _patch_pixi_version_stdout(monkeypatch: pytest.MonkeyPatch):
    original_run = subprocess.run

    def mock_run(cmd, *args, **kwargs):
        if cmd == ["pixi", "--version"]:
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="wrong output", stderr="")
        else:
            return original_run(cmd, *args, **kwargs)

    monkeypatch.setattr("subprocess.run", mock_run)


@pytest.fixture
def _patch_pixi_version(monkeypatch: pytest.MonkeyPatch):
    original_run = subprocess.run

    def mock_run(cmd, *args, **kwargs):
        if cmd == ["pixi", "--version"]:
            result = original_run(cmd, *args, **kwargs)
            assert result.returncode == 0
            assert result.stdout.startswith("pixi ")

            result.stdout = "pixi 0.15.0\n"
            return result
        else:
            return original_run(cmd, *args, **kwargs)

    monkeypatch.setattr("subprocess.run", mock_run)


@pytest.fixture
def _patch_pixi_info_exit_code(monkeypatch: pytest.MonkeyPatch):
    original_run = subprocess.run

    def mock_run(cmd, *args, **kwargs):
        if cmd == ["pixi", "info", "--json"]:
            return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr="error")
        else:
            return original_run(cmd, *args, **kwargs)

    monkeypatch.setattr("subprocess.run", mock_run)


@pytest.fixture
def _patch_pixi_info_stdout(monkeypatch: pytest.MonkeyPatch):
    original_run = subprocess.run

    def mock_run(cmd, *args, **kwargs):
        if cmd == ["pixi", "info", "--json"]:
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="not JSON", stderr="")
        else:
            return original_run(cmd, *args, **kwargs)

    monkeypatch.setattr("subprocess.run", mock_run)


@pytest.fixture
def _patch_pixi_info_no_default_env(monkeypatch: pytest.MonkeyPatch):
    original_run = subprocess.run

    def mock_run(cmd, *args, **kwargs):
        if cmd == ["pixi", "info", "--json"]:
            return subprocess.CompletedProcess(
                cmd,
                returncode=0,
                stdout=json.dumps(
                    {"project_info": {"manifest_path": "/"}, "environments_info": []}
                ),
                stderr="",
            )
        else:
            return original_run(cmd, *args, **kwargs)

    monkeypatch.setattr("subprocess.run", mock_run)
