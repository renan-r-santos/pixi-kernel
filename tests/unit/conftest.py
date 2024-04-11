import subprocess

import pytest


@pytest.fixture()
def _patch_path(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("PATH", raising=False)


@pytest.fixture()
def _patch_pixi_version_exit_code(monkeypatch: pytest.MonkeyPatch):
    def mock_run(cmd, *args, **kwargs):
        if cmd == ["pixi", "--version"]:
            return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr="")
        else:
            return subprocess.run(cmd, *args, **kwargs)

    monkeypatch.setattr("subprocess.run", mock_run)


@pytest.fixture()
def _patch_pixi_version_bad_stdout(monkeypatch: pytest.MonkeyPatch):
    def mock_run(cmd, *args, **kwargs):
        if cmd == ["pixi", "--version"]:
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="wrong output", stderr="")
        else:
            return subprocess.run(cmd, *args, **kwargs)

    monkeypatch.setattr("subprocess.run", mock_run)


@pytest.fixture()
def _patch_pixi_version_value(monkeypatch: pytest.MonkeyPatch):
    original_run = subprocess.run  # Save the original function

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
