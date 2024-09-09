"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import os
from unittest import mock

import pytest
from omegaconf import OmegaConf

from pasha import archive, utils
from pasha.tests import base


class TestArchive(base.TestCase):
    def setUp(self):
        super(TestArchive, self).setUp()

    @mock.patch("pasha.utils.run_command")
    def test_archive(self, mock_exec):
        mock_exec.return_value = (0, "")
        archive.unpack("fake_archive", "fake_rootfs")
        mock_exec.assert_called_once_with(
            [
                "tar",
                "-C",
                "fake_rootfs",
                "--exclude=./dev/*",
                "-zxf",
                "fake_archive",
                "--numeric-owner",
            ]
        )


class TestCompress(base.TestCase):
    def setUp(self):
        super(TestCompress, self).setUp()

    @mock.patch("pasha.utils.run_command")
    @mock.patch("os.path.exists")
    @mock.patch("os.cpu_count")
    def test_compress_with_zstd(self, mock_cpu, mock_os, mock_exec):
        mock_exec.return_value = (0, "")
        mock_os.return_value = True
        mock_cpu.return_value = 1
        archive.compress("fake_archive", compressor="zstd")
        mock_exec.assert_called_once_with(
            "zstd -3 --keep -f -T1 fake_archive", shell=True
        )

    @mock.patch("pasha.utils.run_command")
    @mock.patch("os.path.exists")
    @mock.patch("os.cpu_count")
    def test_compress_with_xz(self, mock_cpu, mock_os, mock_exec):
        mock_exec.return_value = (0, "")
        mock_os.return_value = True
        mock_cpu.return_value = 1
        archive.compress("fake_archive", compressor="xz")
        mock_exec.assert_called_once_with(
            "xz -9 -T1 -f --keep fake_archive", shell=True
        )

    @mock.patch("pasha.utils.run_command")
    @mock.patch("os.path.exists")
    @mock.patch("os.cpu_count")
    def test_compress_with_gz(self, mock_cpu, mock_os, mock_exec):
        mock_exec.return_value = (0, "")
        mock_os.return_value = True
        mock_cpu.return_value = 1
        archive.compress("fake_archive", compressor="gzip")
        mock_exec.assert_called_once_with("gzip -1 --keep -f fake_archive", shell=True)
