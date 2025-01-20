"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import os
import pathlib
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha.modules import apt
from pasha.tests import base


class TestAptModule(base.TestCase):
    def setUp(self):
        super(TestAptModule, self).setUp()
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
        self.stage = OmegaConf.create({})

    @mock.patch("subprocess.run")
    @mock.patch.dict(os.environ, {}, clear=True)
    def test_apt_update(self, mock_run):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        expected_calls = [
            mock.call(
                ["systemd-dissect", "--mount", "--mkdir", "/dev/sda", rootfs],
                check=True,
                capture_output=True,
            ),
            mock.call(
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
                    "--bind",
                    "/sys",
                    "/sys",
                    "--dir",
                    "/run",
                    "--share-net",
                    "--die-with-parent",
                    "--chdir",
                    "/",
                    "apt-get",
                    "--assume-yes",
                    "update",
                ],
                check=True,
                env={"DEBIAN_FRONTEND": "noninteractive"},
            ),
            mock.call(
                ["systemd-dissect", "--umount", rootfs], capture_output=True, check=True
            ),
        ]
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        apt.AptUpdate(self.state, self.config, self.stage).run()
        self.assertEqual(mock_run.call_args_list, expected_calls)

    @mock.patch("subprocess.run")
    @mock.patch.dict(os.environ, {}, clear=True)
    def test_apt_remove(self, mock_run):
        stage = OmegaConf.create({"packages": ["foo"]})
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        expected_calls = [
            mock.call(
                ["systemd-dissect", "--mount", "--mkdir", "/dev/sda", rootfs],
                check=True,
                capture_output=True,
            ),
            mock.call(
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
                    "--bind",
                    "/sys",
                    "/sys",
                    "--dir",
                    "/run",
                    "--share-net",
                    "--die-with-parent",
                    "--chdir",
                    "/",
                    "apt-get",
                    "--assume-yes",
                    "remove",
                    "foo",
                ],
                check=True,
                env={"DEBIAN_FRONTEND": "noninteractive"},
            ),
            mock.call(
                ["systemd-dissect", "--umount", rootfs], capture_output=True, check=True
            ),
        ]
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        apt.AptRemove(self.state, self.config, stage).run()
        self.assertEqual(mock_run.call_args_list, expected_calls)

    @mock.patch("subprocess.run")
    @mock.patch.dict(os.environ, {}, clear=True)
    def test_apt_install(self, mock_run):
        stage = OmegaConf.create({"packages": ["foo"]})
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        expected_calls = [
            mock.call(
                ["systemd-dissect", "--mount", "--mkdir", "/dev/sda", rootfs],
                check=True,
                capture_output=True,
            ),
            mock.call(
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
                    "--bind",
                    "/sys",
                    "/sys",
                    "--dir",
                    "/run",
                    "--share-net",
                    "--die-with-parent",
                    "--chdir",
                    "/",
                    "apt-get",
                    "--assume-yes",
                    "update",
                ],
                check=True,
                env={"DEBIAN_FRONTEND": "noninteractive"},
            ),
            mock.call(
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
                    "--bind",
                    "/sys",
                    "/sys",
                    "--dir",
                    "/run",
                    "--share-net",
                    "--die-with-parent",
                    "--chdir",
                    "/",
                    "apt-get",
                    "--assume-yes",
                    "install",
                    "foo",
                ],
                check=True,
                env={"DEBIAN_FRONTEND": "noninteractive"},
            ),
            mock.call(
                ["systemd-dissect", "--umount", rootfs], capture_output=True, check=True
            ),
        ]
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        apt.AptInstall(self.state, self.config, stage).run()
        self.assertEqual(mock_run.call_args_list, expected_calls)
