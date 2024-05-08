import pathlib
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha import utils
from pasha.modules import user
from pasha.tests import base


class TestUnDeploy(base.TestCase):
    def setUp(self):
        super(TestUnDeploy, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.conf = OmegaConf.create({"name": "fake_name"})
        self.stage = OmegaConf.create(
            {"user": "fake_user", "passwd": "fake_pass", "groups": ["sudo"]}
        )

    @mock.patch("pasha.utils.run_chroot_command")
    def test_create_user(self, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        mock_exec.return_value = (0, "")
        user.User(self.state, self.conf, {}).run()
