"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import pathlib
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha.modules import copy
from pasha.tests import base


class TestCopyCommand(base.TestCase):
    def setUp(self):
        super(TestCopyCommand, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.config = OmegaConf.create(
            {
                "name": "fake_name",
                "architecture": "amd64",
                "params": {
                    "disk": "/dev/sda",
                },
            }
        )
        self.stage = OmegaConf.create({"source": "foo", "dest": "bar"})

    @mock.patch("subprocess.run")
    def test_copy(self, mock_run):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        copy.Copy(self.state, self.config, self.stage).run()
        self.assertEqual(len(mock_run.call_args_list), 3)
