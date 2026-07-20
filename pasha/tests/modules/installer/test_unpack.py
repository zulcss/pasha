"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import os
import pathlib
import tempfile
from unittest import mock
from unittest.mock import call

from omegaconf import OmegaConf

from pasha import utils
from pasha.modules.installer import unpack
from pasha.tests import base


class TestUnpackMount(base.TestCase):
    def setUp(self):
        super(TestUnpackMount, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.config = OmegaConf.create(
            {
                "name": "fake_name",
                "architecture": "amd64",
                "params": {"disk": "/dev/sda", "source": "fake_source.tar.gz"},
            }
        )

        self.stage = OmegaConf.create({})

    @mock.patch("subprocess.run")
    @mock.patch("os.path.exists")
    def test_unpack_module_with_mount(self, mock_exists, mock_run):
        rootfs = self.state.workspace.joinpath("fake_name/rootfs")
        expected_calls = [
            mock.call(["systemctl", "--version"], capture_output=True, text=True),
            mock.call(
                ["systemd-dissect", "--mount", "--mkdir", "/dev/sda", rootfs],
                check=True,
                capture_output=True,
                env={},
            ),
            mock.call(
                [
                    "tar",
                    "-C",
                    rootfs,
                    "--exclude=./dev/*",
                    "-zxf",
                    "fake_source.tar.gz",
                    "--numeric-owner",
                ],
                check=True,
                capture_output=True,
            ),
            mock.call(
                ["systemd-dissect", "--umount", rootfs], capture_output=True, check=True
            ),
        ]
        unpack.Unpack(self.state, self.config, self.stage).run()
        self.assertEqual(mock_run.call_args_list, expected_calls)
