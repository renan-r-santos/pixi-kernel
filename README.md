# Pixi kernel

[![image](https://img.shields.io/pypi/v/pixi-kernel)](https://pypi.python.org/pypi/pixi-kernel)
[![image](https://img.shields.io/pypi/l/pixi-kernel)](https://pypi.python.org/pypi/pixi-kernel)
[![image](https://img.shields.io/pypi/pyversions/pixi-kernel)](https://pypi.python.org/pypi/pixi-kernel)
[![Actions status](https://github.com/renan-r-santos/pixi-kernel/actions/workflows/ci.yml/badge.svg)](https://github.com/renan-r-santos/pixi-kernel/actions)
[![codecov](https://codecov.io/gh/renan-r-santos/pixi-kernel/graph/badge.svg?token=7PCsXpsYSH)](https://codecov.io/gh/renan-r-santos/pixi-kernel)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Per-directory Pixi environments with multi-language Jupyter kernels.

<!--- TODO: add theme selector when supported on PyPI https://github.com/pypi/warehouse/issues/11251 -->

![JupyterLab launcher screen showing Pixi kernel](https://raw.githubusercontent.com/renan-r-santos/pixi-kernel/main/assets/launch-light.png)

Pixi kernel supports Jupyterlab 4, Python 3.9+ and Pixi 0.39.0+ using `pyproject.toml` and
`pixi.toml` configurations.

**Disclaimer**: _This project is not affiliated with Pixi, and not an official Pixi plugin._

## Quick Start

This assumes you want a Python kernel. For other languages, check the [Kernel
support](#kernel-support) table and replace `ipykernel` with the desired kernel package.

1. Install Pixi and `pixi-kernel` alongside JupyterLab using your favorite package manager.
2. Restart JupyterLab.
3. Create a new directory and initialize a Pixi project with `pixi init` and `pixi add ipykernel`.
4. Select the Python Pixi kernel and you are good to go.

See the [Pixi docs](https://pixi.sh/latest/) for more information on how to use Pixi.

## Configuration

### Custom Pixi binary location

By default, `pixi-kernel` will try to find the Pixi binary in this order:

1. Use `shutil.which("pixi")` to find Pixi in your PATH
2. Check for a configuration file at `{user_config_dir}/pixi-kernel/config.toml`
3. Check the default Pixi installation location:
   - Linux/macOS: `$HOME/.pixi/bin/pixi`
   - Windows: `$Env:USERPROFILE\.pixi\bin\pixi.exe`

If you have Pixi installed in a non-standard location, you can create a configuration file to
specify its path:

- **Linux/macOS**: `~/.config/pixi-kernel/config.toml`
- **Windows**: `%APPDATA%\renan-r-santos\pixi-kernel\config.toml`

```toml
pixi-path = "/path/to/your/pixi"
```

## Kernel support

Pixi kernel supports the following kernels:

| Language | Kernel         | Package name                                       |
| -------- | -------------- | -------------------------------------------------- |
| Python   | IPython Kernel | [ipykernel](https://github.com/ipython/ipykernel)  |
| R        | IR Kernel      | [r-irkernel](https://github.com/IRkernel/IRkernel) |

Support for other kernels and languages can be added by opening an issue or a pull request, see
[CONTRIBUTING](CONTRIBUTING.md#adding-support-for-new-kernels).

## Pixi environments

Pixi kernel supports multiple Pixi environments in a single Pixi project. To select a specific
environment, use JupyterLab property inspector, save your notebook and restart your kernel.

![JupyterLab property inspector showing Pixi environment selector](https://raw.githubusercontent.com/renan-r-santos/pixi-kernel/main/assets/env-selector-light.png)

If an environment cannot be determined, Pixi kernel will fallback to the value in the
`PIXI_KERNEL_DEFAULT_ENVIRONMENT` environment variable, if specified. Otherwise, the `default` Pixi
environment will be used.

## JupyterHub deployments with limited permissions

If you're using pixi-kernel on JupyterHub and cannot access the environment where JupyterLab is
installed, you can use the following workaround:

1. Install `pixi-kernel` locally: `pip install pixi-kernel --user`
2. Install Pixi
3. Restart your JupyterLab server

See https://github.com/renan-r-santos/pixi-kernel/issues/62 and
https://github.com/renan-r-santos/pixi-kernel/issues/51 for more information.

## Limitations

Pixi kernel only works with the default environment in VSCode.

## Related

- [Pyproject Local Jupyter Kernel](https://github.com/bluss/pyproject-local-kernel)
- [Poetry-kernel](https://github.com/pathbird/poetry-kernel)
- [Python Local .venv Kernel](https://github.com/goerz/python-localvenv-kernel)
