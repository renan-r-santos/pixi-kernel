# Contributing

Pixi kernel is free and open source software developed under an MIT license. Development occurs at
the [GitHub project](https://github.com/renan-r-santos/pixi-kernel). Contributions are welcome.

Bug reports and feature requests may be made directly on the
[issues](https://github.com/renan-r-santos/pixi-kernel/issues) tab.

To make a pull request, you will need to fork the repo, clone the repo, make the changes, run the
tests, push the changes, and [open a PR](https://github.com/renan-r-santos/pixi-kernel/pulls).

## Cloning the repo

To make a local copy of Pixi kernel, clone the repository with git:

```
git clone https://github.com/renan-r-santos/pixi-kernel.git
```

## Installing system dependencies

Pixi kernel uses `uv` as its packaging and dependency manager. Follow the
[official docs](https://docs.astral.sh/uv) for installing `uv`.

Additionally, Pixi kernel needs `pixi` to run tests. Follow the [official docs](https://pixi.sh)
for installing `pixi`.

Install the project dependencies with:

```
uv sync
```

## Testing and code quality

Pixi kernel uses `pytest`, `unittest` and `tox` to run the tests in the `tests/` directory.
To run all of them, use:

```
uv run tox
```

You can also list and select one specific test by running:

```
uv run tox -l
uv run tox run -e py314-test
```

## Code quality

Pixi kernel uses Ruff and MyPy to ensure a minimum standard of code quality. The code quality
commands are encapsulated with `uv` and `tox`:

```
uv run tox run -e fmt
uv run tox run -e lint
uv run tox run -e type_check
```

## Making a release

1. Bump
   1. Increment version in `pyproject.toml` and `package.json`
   2. Update all lock files by running `uv sync -U` and `pixi update`
   3. Commit with message "chore: Bump version number to X.Y.Z"
   4. Push commit to GitHub
   5. Check [CI](https://github.com/renan-r-santos/pixi-kernel/actions/workflows/ci.yml) to ensure
      all tests pass
2. Tag
   1. Tag commit with "vX.Y.Z"
   2. Push tag to GitHub
   3. Wait for [build](https://github.com/renan-r-santos/pixi-kernel/actions/workflows/release.yml)
      to finish
   4. Check [PyPI](https://pypi.org/project/pixi-kernel/) for good upload
3. Document
   1. Create [GitHub release](https://github.com/renan-r-santos/pixi-kernel/releases) with name
      "Pixi kernel X.Y.Z" and major changes in body
