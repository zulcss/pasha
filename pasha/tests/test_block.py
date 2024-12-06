"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

from unittest import mock

from pasha import block
from pasha.tests import base


class TestBlockDevice(base.TestCase):
    def setUp(self):
        super(TestBlockDevice, self).setUp()

    @mock.patch("subprocess.run")
    def test_create_loopback(self, mock_run):
        block.create_loopback("fake_image")
        self.assertEqual(len(mock_run.call_args_list), 2)

    @mock.patch("subprocess.run")
    def test_remove_loopback(self, mock_run):
        expected_calls = [mock.call(["losetup", "-d", "/dev/looo0"], check=True)]
        block.remove_loopback("/dev/looo0")
        self.assertEqual(mock_run.call_args_list, expected_calls)
