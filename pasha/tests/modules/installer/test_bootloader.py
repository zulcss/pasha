"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import os
import pathlib
import subprocess
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha import exceptions
from pasha.modules.installer.bootloader import BootloaderGrub
from pasha.tests import base


class TestBootloader(base.TestCase):
    def setUp(self):
        super(TestBootloader, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.config = OmegaConf.create(
            {
                "name": "fake_name",
                "params": {
                    "image": "fake_image.img",
                    "mounts": [
                        {"name": "root", "label": "ROOT", "target": "/", "fs": "ext4"}
                    ],
                },
            }
        )
        self.stage = OmegaConf.create({})

    @mock.patch("os.path.exists")
    @mock.patch("subprocess.run")
    @mock.patch("pasha.block.remove_loopback")
    @mock.patch("pasha.block.create_loopback")
    def test_grub_bootloader(self, mock_createloop, mock_removeloop, mock_run, mock_os):
        rootfs = self.state.workspace.joinpath("fake_name/rootfs")
        mock_os.return_value = True
        mock_createloop.return_value = "/dev/loop0"
        expected_calls = [
            mock.call(["udevadm", "settle"], check=True),
            mock.call(
                ["mount", "-t", "ext4", "/dev/disk/by-partlabel/ROOT", rootfs],
                check=True,
            ),
            mock.call(
                ["mount", "-o", "bind", "/dev", rootfs.joinpath("dev")], check=True
            ),
            mock.call(
                ["mount", "-o", "bind", "/proc", rootfs.joinpath("proc")], check=True
            ),
            mock.call(
                ["mount", "-o", "bind", "/sys", rootfs.joinpath("sys")], check=True
            ),
            mock.call(["chroot", rootfs, "update-grub"], check=True),
            mock.call(
                [
                    "chroot",
                    rootfs,
                    "grub-install",
                    "--uefi-secure-boot",
                    "--target=x86_64-efi",
                    "--no-nvram",
                    "--removable",
                ],
                check=True,
            ),
            mock.call(["chroot", rootfs, "update-grub"], check=True),
            mock.call(["umount", "-l", rootfs], check=True),
        ]
        BootloaderGrub(self.state, self.config, self.stage).run()
        self.assertEqual(mock_run.call_args_list, expected_calls)
