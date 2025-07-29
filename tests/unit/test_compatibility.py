import os
import stat
import sys
import tempfile
from pathlib import Path

import pytest
from pixi_kernel.compatibility import find_pixi_binary
from returns.result import Failure, Success


@pytest.fixture
def mock_which(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("shutil.which", lambda cmd: None)


@pytest.fixture
def mock_get_config_file(monkeypatch: pytest.MonkeyPatch):
    path = Path("/does/not/exist/config.toml")
    assert not path.exists()
    monkeypatch.setattr("pixi_kernel.compatibility.get_config_file", lambda: path)


@pytest.fixture
def mock_get_default_pixi_path(monkeypatch: pytest.MonkeyPatch):
    path = Path("/does/not/exist/pixi")
    assert not path.exists()
    monkeypatch.setattr("pixi_kernel.compatibility.get_default_pixi_path", lambda: path)


@pytest.fixture
def pixi_path():
    with tempfile.TemporaryDirectory() as temp_dir:
        pixi_name = "pixi.exe" if sys.platform == "win32" else "pixi"
        pixi_path = Path(temp_dir) / pixi_name
        pixi_path.touch()
        pixi_path.chmod(pixi_path.stat().st_mode | stat.S_IEXEC)
        yield pixi_path


@pytest.fixture
def config_path(monkeypatch: pytest.MonkeyPatch):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        config_path = Path(f.name)
        monkeypatch.setattr("pixi_kernel.compatibility.get_config_file", lambda: config_path)
        yield config_path


@pytest.mark.usefixtures("mock_get_config_file", "mock_get_default_pixi_path")
def test_find_pixi_with_which(pixi_path: Path, monkeypatch: pytest.MonkeyPatch):
    path = os.environ.get("PATH", "")
    new_path = f"{pixi_path.parent}{os.pathsep}{path}"
    monkeypatch.setenv("PATH", new_path)

    result = find_pixi_binary()
    assert isinstance(result, Success)
    assert result.unwrap() == str(pixi_path)


@pytest.mark.usefixtures("mock_which", "mock_get_default_pixi_path")
def test_find_pixi_via_config_file(pixi_path: Path, config_path: Path):
    config_path.write_text(f'pixi-path = "{pixi_path}"')
    result = find_pixi_binary()

    assert isinstance(result, Success)
    assert result.unwrap() == str(pixi_path)


@pytest.mark.usefixtures("mock_which", "mock_get_default_pixi_path")
def test_find_pixi_malformed_toml(config_path: Path):
    config_path.write_text("invalid toml content [[[")
    result = find_pixi_binary()
    assert isinstance(result, Failure)


@pytest.mark.usefixtures("mock_which", "mock_get_default_pixi_path")
def test_find_pixi_missing_key(config_path: Path):
    config_path.write_text('other-key = "value"')
    result = find_pixi_binary()
    assert isinstance(result, Failure)


@pytest.mark.usefixtures("mock_which", "mock_get_default_pixi_path")
def test_find_pixi_invalid_path(config_path: Path):
    invalid_path = Path("/invalid/path/to/pixi")
    assert not invalid_path.exists()

    config_path.write_text(f'pixi-path = "{invalid_path}"')
    result = find_pixi_binary()
    assert isinstance(result, Failure)


@pytest.mark.usefixtures("mock_which", "mock_get_config_file")
def test_find_pixi_via_default_path_success():
    # This should just work in CI and on machines without PIXI_HOME customization
    result = find_pixi_binary()
    assert isinstance(result, Success)


@pytest.mark.usefixtures("mock_which", "mock_get_config_file", "mock_get_default_pixi_path")
def test_find_pixi_not_found_anywhere():
    result = find_pixi_binary()
    assert isinstance(result, Failure)
