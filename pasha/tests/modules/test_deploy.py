import pathlib
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha import utils
from pasha.modules import deploy
from pasha.tests import base


class TestUnDeploy(base.TestCase):
    def setUp(self):
        super(TestUnDeploy, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.conf = OmegaConf.create(
            {"name": "fake_name", "params": {"disk": "/dev/loop0"}}
        )

    @mock.patch("pasha.utils.run_command")
    def test_uddeploy(self, mock_umount):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        mock_umount.return_value = (0, "")
        deploy.Undeploy(self.state, self.conf, {}).run()
        mock_umount.assert_called_once_with(["systemd-dissect", "-u", rootfs])

    @mock.patch("pasha.utils.run_command")
    def test_deploy(self, mock_mount):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        mock_mount.return_value = (0, "")
        deploy.Deploy(self.state, self.conf, {}).run()
        mock_mount.assert_called_once_with(
            ["systemd-dissect", "-m", "/dev/loop0", rootfs]
        )
