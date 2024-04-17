"""Reference: https://github.com/jupyter/jupyter_kernel_test/blob/5f2c65271b48dc95fc75a9585cb1d6db0bb55557/test_xeus_cling.py"""
# ruff: noqa: RUF012

import unittest

import jupyter_kernel_test as jkt
from jupyter_client.kernelspec import NoSuchKernel


class XCpp17Tests(jkt.KernelTests):
    kernel_name = "pixi-kernel-xcpp17"

    @classmethod
    def setUpClass(cls):
        try:
            cls.km, cls.kc = jkt.start_new_kernel(kernel_name=cls.kernel_name)
        except NoSuchKernel:
            raise unittest.SkipTest("Xeus-Cling Kernel not installed") from None

    language_name = "c++"

    file_extension = ".cpp"

    code_hello_world = '#include <iostream>\nstd::cout << "hello, world!" << std::endl;'

    code_stderr = '#include <iostream>\nstd::cerr << "some error" << std::endl;'

    complete_code_samples = ["1", "int j=5"]
    incomplete_code_samples = ["double sqr(double a"]

    code_generate_error = 'throw std::runtime_error("Unknown exception");'

    code_execute_result = [
        {"code": "int j = 5;j", "result": "5"},
    ]


class XCpp14Tests(XCpp17Tests):
    kernel_name = "pixi-kernel-xcpp14"


class XCpp11Tests(XCpp17Tests):
    kernel_name = "pixi-kernel-xcpp11"


if __name__ == "__main__":
    unittest.main()
