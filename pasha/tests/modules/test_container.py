"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import pathlib
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha.modules import container
from pasha.tests import base


class TestContainerBuildModule(base.TestCase):
    def setUp(self):
        super(TestContainerBuildModule, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.config = OmegaConf.create(
            {
                "name": "fake_name",
                "architecture": "amd64",
                "params": {"source": "rootfs.tar.gz"},
            }
        )
        self.stage = OmegaConf.create({"image": "fake_image:latest"})

    @mock.patch("pasha.utils.run_command")
    @mock.patch("os.path.exists")
    @mock.patch("shutil.which")
    @mock.patch("shutil.rmtree")
    def test_container_bulid(self, mock_shutil, mock_which, mock_exists, mock_exec):
        mock_exec.return_value = (0, "")
        mock_exists.return_value = True
        mock_shutil.return_value = True
        container.Container(self.state, self.config, self.stage).run()
        self.assertEqual(mock_exec.call_count, 4)
