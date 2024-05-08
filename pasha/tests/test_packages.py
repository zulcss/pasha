import os
import pathlib
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha import exceptions, packages, utils
from pasha.tests import base


class TestPackages(base.TestCase):
    def setUp(self):
        super(TestPackages, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.config = OmegaConf.create({"name": "fake_name"})

    @mock.patch("pasha.utils.run_command")
    def test_apt_clean(self, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        mock_exec.return_value = (0, "")
        packages.Apt(self.state, self.config).clean()
        mock_exec.assert_called_once_with(
            [
                "bwrap",
                "--bind",
                rootfs,
                "/",
                "--proc",
                "/proc",
                "--dev-bind",
                "/dev",
                "/dev",
                "--dir",
                "/run",
                "--bind",
                "/sys",
                "/sys",
                "--dir",
                "/run",
                "--bind",
                "/tmp",
                "/tmp",
                "--share-net",
                "--die-with-parent",
                "--chdir",
                "/",
                "apt-get",
                "clean",
            ]
        )

    @mock.patch("pasha.utils.run_command")
    @mock.patch.dict(os.environ, {}, clear=True)
    def test_apt_install(self, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        mock_exec.return_value = (0, "")
        packages.Apt(self.state, self.config).install(["foo"])
        mock_exec.assert_called_once_with(
            [
                "bwrap",
                "--bind",
                rootfs,
                "/",
                "--proc",
                "/proc",
                "--dev-bind",
                "/dev",
                "/dev",
                "--dir",
                "/run",
                "--bind",
                "/sys",
                "/sys",
                "--dir",
                "/run",
                "--bind",
                "/tmp",
                "/tmp",
                "--share-net",
                "--die-with-parent",
                "--chdir",
                "/",
                "apt-get",
                "install",
                "-y",
                "foo",
            ],
            env={"DEBIAN_FRONTEND": "noninteractive"},
        )

    @mock.patch("pasha.utils.run_command")
    @mock.patch.dict(os.environ, {}, clear=True)
    def test_apt_remove(self, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        mock_exec.return_value = (0, "")
        packages.Apt(self.state, self.config).remove(["foo"])
        mock_exec.assert_called_once_with(
            [
                "bwrap",
                "--bind",
                rootfs,
                "/",
                "--proc",
                "/proc",
                "--dev-bind",
                "/dev",
                "/dev",
                "--dir",
                "/run",
                "--bind",
                "/sys",
                "/sys",
                "--dir",
                "/run",
                "--bind",
                "/tmp",
                "/tmp",
                "--share-net",
                "--die-with-parent",
                "--chdir",
                "/",
                "apt-get",
                "remove",
                "-y",
                "foo",
            ],
            env={"DEBIAN_FRONTEND": "noninteractive"},
        )

    @mock.patch("pasha.utils.run_command")
    def test_apt_refresh(self, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        mock_exec.return_value = (0, "")
        packages.Apt(self.state, self.config).refresh()
        mock_exec.assert_called_once_with(
            [
                "bwrap",
                "--bind",
                rootfs,
                "/",
                "--proc",
                "/proc",
                "--dev-bind",
                "/dev",
                "/dev",
                "--dir",
                "/run",
                "--bind",
                "/sys",
                "/sys",
                "--dir",
                "/run",
                "--bind",
                "/tmp",
                "/tmp",
                "--share-net",
                "--die-with-parent",
                "--chdir",
                "/",
                "apt-get",
                "update",
            ]
        )

    @mock.patch("pasha.utils.run_command")
    @mock.patch.dict(os.environ, {}, clear=True)
    def test_apt_upgrade(self, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        mock_exec.return_value = (0, "")
        packages.Apt(self.state, self.config).upgrade()
        mock_exec.assert_called_once_with(
            [
                "bwrap",
                "--bind",
                rootfs,
                "/",
                "--proc",
                "/proc",
                "--dev-bind",
                "/dev",
                "/dev",
                "--dir",
                "/run",
                "--bind",
                "/sys",
                "/sys",
                "--dir",
                "/run",
                "--bind",
                "/tmp",
                "/tmp",
                "--share-net",
                "--die-with-parent",
                "--chdir",
                "/",
                "apt-get",
                "upgrade",
                "-y",
            ],
            env={"DEBIAN_FRONTEND": "noninteractive"},
        )

    @mock.patch("pasha.utils.run_command")
    @mock.patch.dict(os.environ, {}, clear=True)
    def test_apt_upgrade(self, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        mock_exec.return_value = (0, "")
        packages.Apt(self.state, self.config).dist_upgrade()
        mock_exec.assert_called_once_with(
            [
                "bwrap",
                "--bind",
                rootfs,
                "/",
                "--proc",
                "/proc",
                "--dev-bind",
                "/dev",
                "/dev",
                "--dir",
                "/run",
                "--bind",
                "/sys",
                "/sys",
                "--dir",
                "/run",
                "--bind",
                "/tmp",
                "/tmp",
                "--share-net",
                "--die-with-parent",
                "--chdir",
                "/",
                "apt-get",
                "dist-upgrade",
                "-y",
            ],
            env={"DEBIAN_FRONTEND": "noninteractive"},
        )
