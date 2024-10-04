from logging import Logger
from pathlib import Path
from typing import Any, Optional, cast

from jupyter_client.kernelspec import KernelSpec
from jupyter_client.provisioning.local_provisioner import LocalProvisioner

from .pixi import ensure_readiness


class PixiKernelProvisioner(LocalProvisioner):  # type: ignore
    async def pre_launch(self, **kwargs: Any) -> dict[str, Any]:
        """Perform any steps in preparation for kernel process launch.

        This includes ensuring Pixi is installed and that a Pixi project is available.
        """
        logger = cast(Logger, self.log)
        kernel_spec = cast(KernelSpec, self.kernel_spec)

        kernel_metadata: Optional[dict[str, str]] = kernel_spec.metadata.get("pixi-kernel")
        if kernel_metadata is None:
            logger.info(
                f"Kernel {kernel_spec.display_name} does not have Pixi Kernel metadata."
                "Falling back to LocalProvisioner."
            )
            return await super().pre_launch(**kwargs)

        required_package = kernel_metadata.get("required-package")
        if required_package is None:
            raise ValueError("Pixi Kernel metadata is missing the 'required-package' key")

        cwd = Path(kwargs.get("cwd", Path.cwd()))
        logger.info(f"The current working directory is {cwd}")

        prefix = ensure_readiness(
            cwd=cwd,
            required_package=required_package,
            kernel_name=kernel_spec.display_name,
        )

        # R kernel needs special treatment
        # https://github.com/renan-r-santos/pixi-kernel/issues/15
        if required_package == "r-irkernel":
            r_libs_path = str(Path(prefix) / "lib" / "R" / "library")
            kernel_spec.env["R_LIBS"] = r_libs_path
            kernel_spec.env["R_LIBS_SITE"] = r_libs_path
            kernel_spec.env["R_LIBS_USER"] = r_libs_path

        logger.info(f"Launching {kernel_spec.display_name}: {kernel_spec.to_dict()}")
        return await super().pre_launch(**kwargs)
