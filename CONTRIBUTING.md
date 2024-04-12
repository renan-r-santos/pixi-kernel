# Contributing

Pixi Kernel is free and open source software developed under an MIT license. Development occurs at
the [GitHub project](https://github.com/renan-r-santos/pixi-kernel). Contributions are welcome.

Bug reports and feature requests may be made directly on the
[issues](https://github.com/renan-r-santos/pixi-kernel/issues) tab.

To make a pull request, you will need to fork the repo, clone the repo, make the changes, run the
tests, push the changes, and [open a PR](https://github.com/renan-r-santos/pixi-kernel/pulls).

## Cloning the repo

To make a local copy of Pixi Kernel, clone the repository with git:

```
git clone https://github.com/renan-r-santos/pixi-kernel.git
```

## Installing from source

Pixi Kernel uses Pixi as its packaging and dependency manager. Install Pixi and then use it to
install Pixi Kernel and its dependencies:

```
pixi install
```

## Testing and code quality

Pixi Kernel uses pytest to run the tests in the `tests/` directory. To run them, use:

```
pixi run test
```

You can also run the tests using a particular Python version:

```
pixi run -e py38 test-py38
```

## Code quality

Pixi Kernel uses Ruff to ensure a minimum standard of code quality. The code quality commands are
encapsulated with Pixi:

```
pixi run format
pixi run lint
```

## Making a release

1. Bump
   1. Increment version in `pyproject.toml` and in `pixi.toml`
   2. Commit with message "Bump version number to X.Y.Z"
   3. Push commit to GitHub
   4. Check [CI](https://github.com/renan-r-santos/pixi-kernel/actions/workflows/ci.yml) to ensure
      all tests pass
2. Tag
   1. Tag commit with "vX.Y.Z"
   2. Push tag to GitHub
   3. Wait for [build](https://github.com/renan-r-santos/pixi-kernel/actions/workflows/release.yml)
      to finish
   4. Check [PyPI](https://pypi.org/project/pixi-kernel/) for good upload
3. Document
   1. Create [GitHub release](https://github.com/renan-r-santos/pixi-kernel/releases) with name
      "Pixi Kernel X.Y.Z" and major changes in body

## Adding support for new kernels

Follow the steps below to add support for a new kernel:

1. In a fresh Pixi environment install your kernel with `pixi install <kernel>`.
2. Copy the new folders created at `.pixi/envs/default/share/jupyter/kernels/` to the `kernels`
   folder and commit the changes.
3. Update the display name, metadata and command arguments in the kernel spec file `kernel.json`.
4. Update the Kernel Support table in the README.
5. Add integration tests for the new kernel in the `tests/integration` folder and commit the
   changes.

You can find below two examples of adding support for new kernels:

Steps 1 and 2:

- [feat: copy original xeus cling kernel spec](https://github.com/renan-r-santos/pixi-kernel/commit/f76c4861041b599b77232988dbc8f1d22edfbf49)
- [feat: copy original bash kernel spec](https://github.com/renan-r-santos/pixi-kernel/commit/93342c82633b4eff8e342a292a143c5f85f829aa)

Steps 3 to 5

- [feat: add support for xeus cling kernel](https://github.com/renan-r-santos/pixi-kernel/commit/8aa9214f220deeb2b133f3ddbfb36e2de2039ca1)
- [feat: add support for bash kernel](https://github.com/renan-r-santos/pixi-kernel/commit/02459c2063a67b3216c9f0fda11b1613583b472c)
