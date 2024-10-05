from typing import cast
from unittest.mock import Mock

import pytest
from jupyter_client.kernelspec import KernelSpec

from pixi_kernel.provisioner import PixiKernelProvisioner


@pytest.fixture
def mock_kernel_spec():
    spec = Mock(spec=KernelSpec)
    spec.metadata = {}
    return spec


@pytest.fixture
def provisioner(mock_kernel_spec):
    provisioner = PixiKernelProvisioner()
    provisioner.kernel_spec = mock_kernel_spec
    return provisioner


@pytest.mark.asyncio
async def test_pre_launch_no_pixi_metadata(provisioner: PixiKernelProvisioner):
    with pytest.raises(ValueError, match="does not have Pixi Kernel metadata"):
        await provisioner.pre_launch()


@pytest.mark.asyncio
async def test_pre_launch_missing_required_package(provisioner: PixiKernelProvisioner):
    kernel_spec = cast(KernelSpec, provisioner.kernel_spec)
    kernel_spec.metadata = {"pixi-kernel": {}}

    with pytest.raises(ValueError, match="missing the 'required-package' key"):
        await provisioner.pre_launch()
