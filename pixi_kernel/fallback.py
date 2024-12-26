import sys
from typing import Any

from ipykernel.ipkernel import IPythonKernel
from ipykernel.kernelapp import IPKernelApp


def start_fallback_kernel(*, message: str, connection_file: str) -> None:
    class FallbackKernel(IPythonKernel):
        def do_execute(self, *args: Any, **kwargs: Any) -> dict[str, str]:
            print(message, file=sys.stderr)
            return {"status": "error", "ename": "PixiKernelError", "evalue": message}

    IPKernelApp.launch_instance(
        argv=["python", "-m", "ipykernel_launcher", "-f", connection_file],
        kernel_class=FallbackKernel,
    )
