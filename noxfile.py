import platform
from typing import List

from nox import options, parametrize
from nox_poetry import Session, session

options.sessions = ["lint", "test", "integration", "coverage"]


@session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
def test(s: Session):
    s.install(".", "pytest", "pytest-cov")
    s.env["COVERAGE_FILE"] = f".coverage.{platform.system()}.{s.python}"
    s.run("python", "-m", "pytest", "--cov", "pixi_kernel")


@session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
def integration(s: Session):
    with s.chdir("tests/integration"):
        s.run("pixi", "run", "--manifest-path=pixi.toml", "python", "kernel.py", external=True)


@session(venv_backend="none")
def coverage(s: Session):
    s.run("coverage", "combine")
    s.run("coverage", "html")
    s.run("coverage", "xml", "--fail-under=60")


@session(venv_backend="none")
@parametrize("command", [["ruff", "check", "."], ["ruff", "format", "--check", "."]])
def lint(s: Session, command: List[str]):
    s.run(*command)


@session(venv_backend="none")
def format(s: Session) -> None:
    s.run("ruff", "check", ".", "--select", "I", "--fix")
    s.run("ruff", "format", ".")
