from pathlib import Path
from typing import Any, List

from jupyter_client.connect import KernelConnectionInfo
from jupyter_client.provisioning import LocalProvisioner

from .pixi import find_project_manifest


class PixiProvisioner(LocalProvisioner):
    async def launch_kernel(self, cmd: List[str], **kwargs: Any) -> KernelConnectionInfo:
        """Launch a kernel with Pixi."""
        pixi_kernel_metadata = self.kernel_spec.metadata.get("pixi-kernel", None)
        if pixi_kernel_metadata is None:
            self.log.info(
                f"[pixi-kernel] {self.kernel_spec} is not a pixi-kernel, falling back to local "
                "provisioner."
            )
            return await super().launch_kernel(cmd, **kwargs)

        cwd = kwargs.get("cwd", None)
        if cwd is None:
            cwd = Path.cwd()
            self.log.warning(f"[pixi-kernel] cwd not found in {kwargs}, using default {cwd}")

        manifest_path = find_project_manifest(
            cwd=Path(cwd),
            package_name=pixi_kernel_metadata["package-name"],
            kernel_display_name=self.kernel_spec.display_name,
            logger=self.log,
        )
        self.log.info(f"[pixi-kernel] project manifest path: {manifest_path}")

        index = cmd.index("--manifest-path=")
        cmd[index] = f"--manifest-path={manifest_path}"

        self.log.info(f"[pixi-kernel] launching kernel: {cmd}")
        return await super().launch_kernel(cmd, **kwargs)
