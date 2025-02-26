"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

from unittest import mock

from pasha import udev
from pasha.tests import base


class TestUdev(base.TestCase):
    def setUp(self):
        super(TestUdev, self).setUp()

    @mock.patch("subprocess.run")
    def test_udev_settle(self, mock_run):
        expected_calls = [mock.call(["udevadm", "settle"], check=True)]
        udev.settle()
        self.assertEqual(mock_run.call_args_list, expected_calls)
