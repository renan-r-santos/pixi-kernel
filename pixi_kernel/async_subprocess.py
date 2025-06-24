import platform
import subprocess
from asyncio import SelectorEventLoop, create_subprocess_exec, get_running_loop
from asyncio.subprocess import PIPE
from typing import Any


async def subprocess_exec(program: str, *args: str, **kwargs: Any) -> tuple[int, str, str]:
    # The SelectorEventLoop does not support asyncio.subprocess
    # https://github.com/renan-r-santos/pixi-kernel/issues/39
    if isinstance(get_running_loop(), SelectorEventLoop) and platform.system() == "Windows":
        result = subprocess.run([program, *args], capture_output=True, text=True, **kwargs)  # noqa: ASYNC221
        return result.returncode, result.stdout, result.stderr
    else:
        process = await create_subprocess_exec(program, *args, stdout=PIPE, stderr=PIPE, **kwargs)
        stdout_bytes, stderr_bytes = await process.communicate()
        assert process.returncode is not None
        stdout, stderr = stdout_bytes.decode("utf-8"), stderr_bytes.decode("utf-8")
        return process.returncode, stdout, stderr
