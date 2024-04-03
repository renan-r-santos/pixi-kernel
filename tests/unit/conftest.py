import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Union

import pytest


@contextmanager
def _cwd(new_dir: Union[str, Path]):
    original_dir = Path.cwd().resolve()
    try:
        os.chdir(new_dir)
        yield
    finally:
        os.chdir(original_dir)


@pytest.fixture()
def cwd():
    return _cwd


@pytest.fixture()
def _patch_path(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("PATH", raising=False)


@pytest.fixture()
def _patch_subprocess_exit_code(monkeypatch: pytest.MonkeyPatch):
    def mock_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, returncode=1, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)


@pytest.fixture()
def _patch_subprocess_stdout(monkeypatch: pytest.MonkeyPatch):
    def mock_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, returncode=0, stdout="wrong output", stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)


@pytest.fixture()
def _patch_pixi_version(monkeypatch: pytest.MonkeyPatch):
    original_run = subprocess.run  # Save the original function

    def mock_run(*args, **kwargs):
        result = original_run(*args, **kwargs)
        assert result.returncode == 0
        assert result.stdout.startswith("pixi ")

        result.stdout = "pixi 0.15.0\n"
        return result

    monkeypatch.setattr("subprocess.run", mock_run)
