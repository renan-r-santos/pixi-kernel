# Pixi Kernel

[![GitHub Actions][github-actions-badge]](https://github.com/renan-r-santos/pixi-kernel/actions)
[![codecov](https://codecov.io/gh/renan-r-santos/pixi-kernel/graph/badge.svg?token=7PCsXpsYSH)](https://codecov.io/gh/renan-r-santos/pixi-kernel)
[![Pixi Badge][pixi-badge]](https://pixi.sh)
[![Ruff][ruff-badge]](https://github.com/astral-sh/ruff)

[github-actions-badge]: https://github.com/renan-r-santos/pixi-kernel/actions/workflows/ci.yml/badge.svg
[pixi-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/prefix-dev/pixi/main/assets/badge/v0.json&style=flat-square
[ruff-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json

Per-directory Pixi environments with multi-language Jupyter kernels.

<!--- TODO: add theme selector when supported on PyPI https://github.com/pypi/warehouse/issues/11251 -->

![JupyterLab launcher screen showing Pixi Kernel](https://raw.githubusercontent.com/renan-r-santos/pixi-kernel/main/assets/launch-light.png)

Pixi Kernel supports Python 3.9+ and Pixi 0.30.0+ using `pyproject.toml` and `pixi.toml` configurations.

**Disclaimer**: _This project is not affiliated with Pixi, and not an official Pixi plugin._

## Quick Start

This assumes you want a Python kernel. For other languages, check the [Kernel
support](#kernel-support) table and replace `ipykernel` with the desired kernel package.

1. Install Pixi and `pixi-kernel` alongside JupyterLab using your favorite package manager.
2. Restart JupyterLab.
3. Create a new directory and initialize a Pixi project with `pixi init` and `pixi add ipykernel`.
4. Restart the kernel and you are good to go.

See the [Pixi docs](https://pixi.sh/latest/) for more information on how to use Pixi.

## Kernel support

Pixi Kernel supports the following kernels:

| Language | Kernel         | Package name                                       |
| -------- | -------------- | -------------------------------------------------- |
| Python   | IPython Kernel | [ipykernel](https://github.com/ipython/ipykernel)  |
| R        | IR Kernel      | [r-irkernel](https://github.com/IRkernel/IRkernel) |

Support for other kernels and languages can be added by opening an issue or a pull request, see [CONTRIBUTING](CONTRIBUTING.md#adding-support-for-new-kernels).

## Limitations

Pixi Kernel only works with the default environment. If you have an
idea how to support this see [this issue](https://github.com/renan-r-santos/pixi-kernel/issues/20)
or see [CONTRIBUTING](CONTRIBUTING.md#adding-support-for-new-kernels).

## Related

- [Pyproject Local Jupyter Kernel](https://github.com/bluss/pyproject-local-kernel)
- [Poetry-kernel](https://github.com/pathbird/poetry-kernel)
- [Python Local .venv Kernel](https://github.com/goerz/python-localvenv-kernel)
