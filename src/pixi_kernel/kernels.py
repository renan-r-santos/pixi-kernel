import logging
import platform
import signal
import subprocess
import sys

from ipykernel.ipkernel import IPythonKernel
from ipykernel.kernelapp import IPKernelApp

logger = logging.getLogger(__name__)


def start_pixi_kernel(manifest_path: str):
    cmd = [
        "pixi",
        "run",
        "--manifest-path",
        manifest_path,
        "python",
        "-m",
        "ipykernel_launcher",
        *sys.argv[1:],
    ]
    logger.info(f"Starting kernel: {cmd}")
    try:
        process = subprocess.Popen(cmd)

        if platform.system() == "Windows":
            forward_signals = set(signal.Signals) - {
                signal.CTRL_BREAK_EVENT,
                signal.CTRL_C_EVENT,
                signal.SIGBREAK,
                signal.SIGTERM,
            }
        else:
            forward_signals = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}

        def handle_signal(sig, _frame):
            process.send_signal(sig)

        for sig in forward_signals:
            signal.signal(sig, handle_signal)

        exit_code = process.wait()
        if exit_code != 0:
            logger.error(f"kernel exited with error code: {exit_code}")
    except Exception as exception:
        logger.error(f"kernel could not be started: {exception}")


def start_fallback_kernel(message: str):
    class FallbackKernel(IPythonKernel):
        def do_execute(self, *args, **kwargs):
            print(message, file=sys.stderr)
            return super().do_execute(*args, **kwargs)

    IPKernelApp.launch_instance(kernel_class=FallbackKernel)
