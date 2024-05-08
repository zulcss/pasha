from unittest import mock

from pasha import exceptions, mount, utils
from pasha.tests import base


class TestMount(base.TestCase):
    def test_mount(self):
        with mock.patch.object(utils, "run_command") as execute:
            execute.return_value = (0, "fake_output")
            ret = mount.mount("fake_image", "fake_root")
            execute.assert_called_once_with(
                ["systemd-dissect", "-m", "fake_image", "fake_root"]
            )

    def test_umount(self):
        with mock.patch.object(utils, "run_command") as execute:
            execute.return_value = (0, "fake_output")
            ret = mount.umount("fake_image")
            execute.assert_called_once_with(["systemd-dissect", "-u", "fake_image"])

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
