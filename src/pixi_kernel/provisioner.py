import logging
import os
from pathlib import Path
from typing import Any, Optional, cast

from jupyter_client.kernelspec import KernelSpec
from jupyter_client.provisioning.local_provisioner import LocalProvisioner

from .pixi import ensure_readiness

logger = logging.getLogger(__name__)


class PixiKernelProvisioner(LocalProvisioner):  # type: ignore
    async def pre_launch(self, **kwargs: Any) -> dict[str, Any]:
        """Perform any steps in preparation for kernel process launch.

        This includes ensuring Pixi is installed and that a Pixi project is available.
        """
        kernel_spec = cast(KernelSpec, self.kernel_spec)

        kernel_metadata: Optional[dict[str, str]] = kernel_spec.metadata.get("pixi-kernel")
        if kernel_metadata is None:
            raise ValueError(
                f"Kernel {kernel_spec.display_name} uses the PixiKernelProvisioner but it"
                "does not have Pixi Kernel metadata."
            )

        required_package = kernel_metadata.get("required-package")
        if required_package is None:
            raise ValueError("Pixi Kernel metadata is missing the 'required-package' key")

        cwd = Path(kwargs.get("cwd", Path.cwd()))
        logger.info(f"JupyterLab provided this value for cwd: {kwargs.get('cwd', None)}")
        logger.info(f"The current working directory is {cwd}")

        env: dict[str, str] = kwargs.get("env", os.environ)
        pixi_environment = ensure_readiness(
            cwd=cwd.resolve(),
            env=env,
            required_package=required_package,
            kernel_name=kernel_spec.display_name,
        )

        # R kernel needs special treatment
        # https://github.com/renan-r-santos/pixi-kernel/issues/15
        if required_package == "r-irkernel":
            r_libs_path = str(Path(pixi_environment.prefix) / "lib" / "R" / "library")
            kernel_spec.env["R_LIBS"] = r_libs_path
            kernel_spec.env["R_LIBS_SITE"] = r_libs_path
            kernel_spec.env["R_LIBS_USER"] = r_libs_path

        logger.info(f"Launching {kernel_spec.display_name}: {kernel_spec.to_dict()}")
        return await super().pre_launch(**kwargs)
