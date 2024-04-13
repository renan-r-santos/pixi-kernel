import re
from pathlib import Path
from typing import Any, Dict

from jupyter_client.provisioning import LocalProvisioner

from .pixi import find_project_manifest

pattern = re.compile(r"\{([A-Za-z0-9_-]+)\}")


class PixiProvisioner(LocalProvisioner):
    async def pre_launch(self, **kwargs: Any) -> Dict[str, Any]:
        """Launch a kernel with Pixi."""
        pixi_kernel_metadata = self.kernel_spec.metadata.get("pixi-kernel", None)
        if pixi_kernel_metadata is None:
            self.log.info(
                f"[pixi-kernel] {self.kernel_spec} is not a pixi-kernel, falling back to local "
                "provisioner."
            )
            return await super().pre_launch(**kwargs)

        cwd = kwargs.get("cwd", None)
        if cwd is None:
            cwd = Path.cwd()
            self.log.warning(f"[pixi-kernel] cwd not found in {kwargs}, using default {cwd}")

        manifest_path = find_project_manifest(
            cwd=Path(cwd).absolute(),
            package_name=pixi_kernel_metadata["package-name"],
            kernel_display_name=self.kernel_spec.display_name,
            logger=self.log,
        )
        self.log.info(f"[pixi-kernel] project manifest path: {manifest_path}")

        ns: Dict[str, Any] = {
            "manifest-path": str(manifest_path),
            "manifest-path-parent": str(manifest_path.parent),
        }

        def from_ns(match: Any) -> Any:
            """Get the key out of ns if it's there, otherwise no change."""
            return ns.get(match.group(1), match.group())

        self.kernel_spec.argv = [pattern.sub(from_ns, arg) for arg in self.kernel_spec.argv]
        self.kernel_spec.env = {
            k: pattern.sub(from_ns, v) for k, v in self.kernel_spec.env.items()
        }

        self.log.info(f"[pixi-kernel] launching kernel with spec: {self.kernel_spec.to_json()}")
        return await super().pre_launch(**kwargs)
