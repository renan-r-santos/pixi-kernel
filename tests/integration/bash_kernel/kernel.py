"""Reference: https://github.com/Calysto/calysto_bash/blob/dfa6833187e1fe9d9c229fd7bcc839fd7813d74b/test_bash_kernel.py"""
# ruff: noqa: RUF012

import os
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Union

import jupyter_kernel_test as jkt


@contextmanager
def cwd(new_dir: Union[str, Path]):
    original_dir = Path.cwd().resolve()
    try:
        os.chdir(new_dir)
        yield
    finally:
        os.chdir(original_dir)


class BashKernelTests(jkt.KernelTests):
    # the kernel to be tested
    # this is the normally the name of the directory containing the
    # kernel.json file - you should be able to do
    # `jupyter console --kernel KERNEL_NAME`
    kernel_name = "pixi-kernel-bash"

    # Everything else is OPTIONAL

    # the name of the language the kernel executes
    # checked against language_info.name in kernel_info_reply
    language_name = "bash"

    # the normal file extension (including the leading dot) for this language
    # checked against language_info.file_extension in kernel_info_reply
    file_extension = ".sh"

    code_hello_world = "echo 'hello, world'"

    completion_samples = [
        {
            "text": "fdis",
            "matches": {"fdisk"},
        },
    ]


if __name__ == "__main__":
    with cwd(Path(__file__).parent.resolve()):
        unittest.main()
