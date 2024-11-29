"""User-friendly error messages used by Pixi Kernel."""

PIXI_NOT_FOUND = """
Pixi was not detected in your system but it is required for running the {kernel_name} kernel.
Please follow the steps below to install Pixi:
    1. Visit the Pixi installation guide at https://pixi.sh/latest/
    2. After installation, restart JupyterLab.
    3. Ensure that Pixi was added to your PATH by checking the output of 'which pixi'.

If you continue to face issues, report them at https://github.com/renan-r-santos/pixi-kernel/issues
"""

PIXI_VERSION_ERROR = """
Pixi was detected in your system but it appears to be corrupted.
To run the {kernel_name} kernel, please follow the steps below to reinstall Pixi:
    1. Visit the Pixi installation guide at https://pixi.sh/latest/
    2. After installation, restart JupyterLab.
    3. Ensure that Pixi is working by running 'pixi --version' in your terminal.

If you continue to face issues, report them at https://github.com/renan-r-santos/pixi-kernel/issues
"""

PIXI_OUTDATED = """
Pixi was detected in your system but it appears to be outdated. You need at least Pixi 
{minimum_version} in order to run the {kernel_name} kernel. In your terminal, run 
'pixi self-update' to update Pixi to the latest version and restart your kernel.

If you continue to face issues, report them at https://github.com/renan-r-santos/pixi-kernel/issues
"""

PIXI_KERNEL_NOT_FOUND = """
To run the {kernel_name} kernel, you need to add the {required_package} package to 
your project dependencies. You can do this by running 'pixi add {required_package}'
in your project directory and restarting your kernel. Make sure the prefix
{prefix}
points to the correct Pixi environment.

If you continue to face issues, report them at https://github.com/renan-r-santos/pixi-kernel/issues
"""
