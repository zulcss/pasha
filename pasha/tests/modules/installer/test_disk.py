"""
Copyright (c) 2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import os
import pathlib
import tempfile
from unittest import mock
from unittest.mock import call

import pytest
from omegaconf import OmegaConf

from pasha import utils
from pasha.modules.installer import disk
from pasha.tests import base


class TestDiskPartition(base.TestCase):
    def setUp(self):
        super(TestDiskPartition, self).setUp()
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
        self.stage = OmegaConf.create(
            {
                "slices": [
                    {
                        "name": "EFI",
                        "start": "0%",
                        "end": "128MB",
                        "flags": ["boot", "esp"],
                        "id": "c12a7328-f81f-11d2-ba4b-00a0c93ec93b",
                    },
                    {
                        "name": "BOOT",
                        "start": "128M",
                        "end": "640M",
                        "flags": [],
                        "id": "bc13c2ff-59e6-4262-a352-b275fd6f7172",
                    },
                    {
                        "name": "ROOT",
                        "start": "640MB",
                        "end": "100%",
                        "flags": [],
                        "id": "",
                    },
                ]
            }
        )

    @mock.patch("subprocess.run")
    @mock.patch("os.path.exists")
    @mock.patch("shutil.which")
    def test_disk_partition_with_block_device(self, mock_which, mock_os, mock_run):
        expected_calls = [
            call(
                [
                    "parted",
                    "-a",
                    "optimal",
                    "-s",
                    "/dev/sda",
                    "--",
                    "mklabel",
                    "gpt",
                    "mkpart",
                    "EFI",
                    "0%",
                    "128MB",
                    "set",
                    "1",
                    "boot",
                    "on",
                    "set",
                    "1",
                    "esp",
                    "on",
                    "mkpart",
                    "BOOT",
                    "128M",
                    "640M",
                    "mkpart",
                    "ROOT",
                    "640MB",
                    "100%",
                ],
                capture_output=True,
                check=True,
            ),
            call(
                [
                    "sfdisk",
                    "--part-type",
                    "/dev/sda",
                    "1",
                    "c12a7328-f81f-11d2-ba4b-00a0c93ec93b",
                ],
                capture_output=True,
                check=True,
            ),
            call(
                [
                    "sfdisk",
                    "--part-type",
                    "/dev/sda",
                    "2",
                    "bc13c2ff-59e6-4262-a352-b275fd6f7172",
                ],
                capture_output=True,
                check=True,
            ),
            call(["parted", "/dev/sda", "print"], check=True),
        ]
        mock_which.return_value = True
        disk.Parted(self.state, self.config, self.stage).run()
        self.assertEqual(mock_run.call_args_list, expected_calls)


class TestDiskFilesystem(base.TestCase):
    def setUp(self):
        super(TestDiskFilesystem, self).setUp()
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
        self.stage = OmegaConf.create(
            {
                "filesystems": [
                    {"name": "EFI", "label": "EFI", "fs": "vfat", "options": []}
                ]
            }
        )

    @mock.patch("subprocess.run")
    @mock.patch("os.path.exists")
    def test_create_filesysems_with_block(self, mock_exist, mock_run):
        expected_calls = [
            mock.call(
                ["mkfs.vfat", "-F", "32", "-n", "EFI", "/dev/sda1"],
                capture_output=True,
                check=True,
            ),
            mock.call(["parted", "/dev/sda", "print"], check=True),
        ]
        disk.Filesystem(self.state, self.config, self.stage).run()
        self.assertEqual(mock_run.call_args_list, expected_calls)
