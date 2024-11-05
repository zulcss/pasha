"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import subprocess
from unittest import mock

from pasha import block
from pasha.tests import base


class TestBlockDevice(base.TestCase):
    def setUp(self):
        super(TestBlockDevice, self).setUp()

    @mock.patch("subprocess.run")
    def test_create_loopback(self, mock_run):
        expected_calls = [
            mock.call(
                ["losetup", "--find", "--show", "--partscan", "fake_image"],
                stdout=-1,
                encoding="utf-8",
                check=True,
            )
        ]
        block.create_loopback("fake_image")
        self.assertEqual(mock_run.call_args_list, expected_calls)

    @mock.patch("subprocess.run")
    def test_remove_loopback(self, mock_run):
        expected_calls = [mock.call(["losetup", "-d", "/dev/looo0"], check=True)]
        block.remove_loopback("/dev/looo0")
        self.assertEqual(mock_run.call_args_list, expected_calls)
