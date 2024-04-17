import logging
import os
import signal
import subprocess
import sys
import typing
from pathlib import Path
from types import FrameType

from ipykernel.ipkernel import IPythonKernel
from ipykernel.kernelapp import IPKernelApp

from .pixi import PixiDiscoveryError, find_project_manifest

logger = logging.getLogger(__name__)


def start_fallback_kernel(message: str) -> None:
    class FallbackMessageKernel(IPythonKernel):
        @typing.no_type_check
        def do_execute(self, *args, **kwargs):
            print(message, file=sys.stderr)
            return {"status": "error", "ename": "PixiDiscoveryError", "evalue": message}

    for arg in sys.argv:
        if Path(arg).suffix == ".json" and Path(arg).exists():
            connection_file = arg
            break
    else:
        raise ValueError("connection file not found in sys.argv")

    return IPKernelApp.launch_instance(
        argv=["python", "-m", "ipykernel_launcher", "-f", connection_file],
        kernel_class=FallbackMessageKernel,
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[pixi-kernel]: %(message)s")

    package_name = sys.argv[1]
    kernel_display_name = sys.argv[2]

    try:
        manifest_path = find_project_manifest(
            cwd=Path.cwd(),
            package_name=package_name,
            kernel_display_name=kernel_display_name,
        )
    except PixiDiscoveryError as exception:
        return start_fallback_kernel(exception.message)

    logger.info(f"project manifest path: {manifest_path}")

    args = ["pixi", "run", f"--manifest-path={manifest_path}", *sys.argv[3:]]
    env = os.environ.copy()

    # To keep the R kernel constrained to the project's R libraries, set the library paths
    if package_name == "r-irkernel":
        r_libs_path = str(manifest_path.parent / ".pixi/envs/default/lib/R/library")
        env["R_LIBS"] = r_libs_path
        env["R_LIBS_SITE"] = r_libs_path
        env["R_LIBS_USER"] = r_libs_path

    logger.info(f"launching {kernel_display_name} kernel with {args}")

    if sys.platform == "win32":
        process = subprocess.Popen(args, env=env)

        forward_signals = set(signal.Signals) - {
            signal.CTRL_BREAK_EVENT,
            signal.CTRL_C_EVENT,
            signal.SIGBREAK,
            signal.SIGTERM,
        }

        def handle_signal(sig: int, frame: FrameType | None) -> None:
            process.send_signal(sig)

        for sig in forward_signals:
            signal.signal(sig, handle_signal)

        sys.exit(process.wait())
    else:
        os.execvpe("pixi", args, env)


if __name__ == "__main__":
    main()
