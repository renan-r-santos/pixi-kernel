import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional, cast

from jupyter_client.kernelspec import KernelSpec
from jupyter_client.provisioning.local_provisioner import LocalProvisioner
from returns.result import Failure

from .readiness import verify_env_readiness

logger = logging.getLogger(__name__)


class PixiKernelProvisioner(LocalProvisioner):  # type: ignore[misc]
    async def _launch_fallback_kernel(self, *, message: str, **kwargs: Any) -> dict[str, Any]:
        kernel_spec = cast(KernelSpec, self.kernel_spec)
        kernel_spec.argv = [sys.executable, "-m", "pixi_kernel", "{connection_file}", message]
        logger.info(f"Launching fallback kernel: {kernel_spec.to_dict()}")
        return await super().pre_launch(**kwargs)

    async def pre_launch(self, **kwargs: Any) -> dict[str, Any]:
        kernel_spec = cast(KernelSpec, self.kernel_spec)

        # Reload argv from the original kernel spec to avoid side effects from previous launches
        kernel_spec.argv = KernelSpec.from_resource_dir(kernel_spec.resource_dir).argv

        kernel_metadata: Optional[dict[str, str]] = kernel_spec.metadata.get("pixi-kernel")
        if kernel_metadata is None:
            message = (
                f"Kernel {kernel_spec.display_name} uses the PixiKernelProvisioner but it"
                "does not have any Pixi kernel metadata."
            )
            return await self._launch_fallback_kernel(message=message, **kwargs)

        required_package = kernel_metadata.get("required-package")
        if required_package is None:
            message = (
                f"Kernel {kernel_spec.display_name} is missing the 'required-package' metadata."
            )
            return await self._launch_fallback_kernel(message=message, **kwargs)

        cwd = Path(kwargs.get("cwd", Path.cwd()))
        logger.info(f"Working directory: {cwd} (provided by JupyterLab: {kwargs.get('cwd')})")

        env: dict[str, str] = kwargs.get("env", os.environ.copy())

        # https://github.com/jupyterlab/jupyterlab/issues/16282
        notebook_path = env.get("JPY_SESSION_NAME")
        if notebook_path is None:
            logger.error(
                "Failed to get notebook path from JPY_SESSION_NAME variable."
                "Falling back to the default environment."
            )
            environment_name = "default"
        else:
            try:
                notebook = json.loads(Path(notebook_path).read_text())
                environment_name = notebook["metadata"]["pixi-kernel"]["environment"]
            except Exception as exception:
                logger.error(
                    f"Failed to get Pixi environment name from notebook metadata."
                    f"Falling back to default environment. {exception}"
                )
                environment_name = "default"

        result = await verify_env_readiness(
            environment_name=environment_name,
            cwd=cwd.resolve(),
            env=env,
            required_package=required_package,
            kernel_name=kernel_spec.display_name,
        )
        if isinstance(result, Failure):
            return await self._launch_fallback_kernel(message=result.failure(), **kwargs)

        pixi_environment = result.unwrap()

        # Update kernel spec command line arguments: `argv[:2] = ["pixi", "run"]`
        argv = kernel_spec.argv
        kernel_spec.argv = argv[:2] + ["--environment", environment_name] + argv[2:]

        # R kernel needs special treatment
        # https://github.com/renan-r-santos/pixi-kernel/issues/15
        if required_package == "r-irkernel":
            r_libs_path = str(Path(pixi_environment.prefix) / "lib" / "R" / "library")
            kernel_spec.env["R_LIBS"] = r_libs_path
            kernel_spec.env["R_LIBS_SITE"] = r_libs_path
            kernel_spec.env["R_LIBS_USER"] = r_libs_path

        logger.info(f"Launching {kernel_spec.display_name}: {kernel_spec.to_dict()}")
        return await super().pre_launch(**kwargs)
