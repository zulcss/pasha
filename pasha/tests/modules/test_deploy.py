"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import pathlib
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha import udev, utils
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
    @mock.patch("pasha.udev.settle")
    def test_undeploy(self, mock1, mock2):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        utils.run_command.return_value = (0, "")
        deploy.Undeploy(self.state, self.conf, {}).run()
        utils.run_command.assert_called_once_with(["systemd-dissect", "-u", rootfs])
        udev.settle.assert_called_once_with()

    @mock.patch("pasha.utils.run_command")
    @mock.patch("pasha.udev.settle")
    def test_deploy(self, mock1, mock2):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        utils.run_command.return_value = (0, "")
        deploy.Deploy(self.state, self.conf, {}).run()
        utils.run_command.assert_called_once_with(
            ["systemd-dissect", "-m", "/dev/loop0", rootfs]
        )
        udev.settle.assert_called_once_with()
