"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

from unittest import mock

from pasha import exceptions, mount, udev, utils
from pasha.tests import base


class TestMount(base.TestCase):
    @mock.patch("pasha.utils.run_command")
    @mock.patch("pasha.udev.settle")
    def test_mount(self, mock1, mock2):
        utils.run_command.return_value = (0, "fake_output")
        mount.mount("fake_image", "fake_root")
        utils.run_command.assert_called_once_with(
            ["systemd-dissect", "-m", "fake_image", "fake_root"]
        )
        udev.settle.assert_called_once_with()

    @mock.patch("pasha.utils.run_command")
    @mock.patch("pasha.udev.settle")
    def test_umount(self, mock1, mock2):
        utils.run_command.return_value = (0, "fake_output")
        mount.umount("fake_image")
        utils.run_command.assert_called_once_with(
            ["systemd-dissect", "-u", "fake_image"]
        )
        udev.settle.assert_called_once_with()

    def test_mount_fail(self):
        with mock.patch.object(utils, "run_command") as execute:
            execute.return_value = (1, "fake_output")
            self.assertRaises(
                exceptions.CommandError, mount.mount, "fake_image", "fake_root"
            )

    def test_umount_fail(self):
        with mock.patch.object(utils, "run_command") as execute:
            execute.return_value = (1, "fake_output")
            self.assertRaises(exceptions.CommandError, mount.umount, "fake_root")
