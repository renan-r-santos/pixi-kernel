"""User-friendly error messages used by the Pixi Kernel."""

PIXI_NOT_FOUND = """Pixi was not detected in your system but it is required for running the {kernel_display_name} kernel.
Please follow the steps below to install Pixi:
    1. Visit the Pixi installation guide at https://pixi.sh/latest/
    2. After installation, restart JupyterLab.
    3. Ensure that Pixi was added to your PATH by typing 'which pixi' in your terminal and checking if the Pixi directory is listed.

If you continue to face issues, please report them at https://github.com/renan-r-santos/pixi-kernel/issues
"""

PIXI_VERSION_ERROR = """Pixi was detected in your system but it appears to be corrupted. To run the {kernel_display_name} kernel, 
please follow the steps below to reinstall Pixi:
    1. Visit the Pixi installation guide at https://pixi.sh/latest/
    2. After installation, restart JupyterLab.
    3. Ensure that Pixi is working by typing 'pixi --version' in your terminal and checking if the version string is listed.

If you continue to face issues, please report them at https://github.com/renan-r-santos/pixi-kernel/issues
"""

PIXI_VERSION_NOT_SUPPORTED = """Pixi was detected in your system but it appears to be outdated.
You need at least Pixi {minimum_version} in order to run the {kernel_display_name} kernel.
In your terminal, type 'pixi self-update' to update Pixi to the latest version.

If you continue to face issues, please report them at https://github.com/renan-r-santos/pixi-kernel/issues
"""

PIXI_MANIFEST_NOT_FOUND = """Pixi Kernel could not find a project manifest file in
the current working directory {cwd} nor in any of its parents.
Make sure you initialize a Pixi project by running 'pixi init' in the project directory.

If you continue to face issues, please report them at https://github.com/renan-r-santos/pixi-kernel/issues
"""

PIXI_KERNEL_NOT_FOUND = """To run the {kernel_display_name} kernel, you need to add the {package_name} package to your project dependencies.
You can do this by running 'pixi add {package_name}' in your project directory and trying again.

If you continue to face issues, please report them at https://github.com/renan-r-santos/pixi-kernel/issues
"""
