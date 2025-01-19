"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import pathlib
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha import bootloader
from pasha.context import Context
from pasha.tests import base


class TestUBootloader(base.TestCase):
    def setUp(self):
        super(TestUBootloader, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.config = OmegaConf.create(
            {
                "name": "fake_name",
                "architecture": "amd64",
                "params": {
                    "disk": "fake_image.img",
                },
            }
        )
        self.stage = OmegaConf.create({})

    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    def test_systemd_boot_install(self, mock_which, mock_run):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        expected_calls = [
            mock.call(
                [
                    "bootctl",
                    "install",
                    f"--root={rootfs}",
                    "--no-variables",
                    "--entry-token",
                    "os-id",
                ],
                check=True,
                capture_output=True,
            )
        ]
        context = Context(self.state, self.config, self.stage)
        bootloader.install_systemd_boot(context, ostree=False)
        self.assertEqual(mock_run.call_args_list, expected_calls)
