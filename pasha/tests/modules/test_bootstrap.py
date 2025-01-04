"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import os
import pathlib
import tempfile
from unittest import mock

import pytest
from omegaconf import OmegaConf

from pasha.modules import bootstrap
from pasha.tests import base


class TestBootstrapModule(base.TestCase):
    def setUp(self):
        super(TestBootstrapModule, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.config = OmegaConf.create({"name": "fake_name", "architecture": "amd64"})
        self.stage = OmegaConf.create(
            {"target": "fake_target", "suite": "bookworm", "architecture": "amd64"}
        )
        self.cwd = os.path.join(os.getcwd(), "mmdebstrap.log")

    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    def test_bootstrap(self, mock_which, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        mock_exec.return_value = (0, "")
        mock_which.return_value = "/usr/bin/mmdebstrap"
        bootstrap.Bootstrap(self.state, self.config, self.stage).run()
        mock_exec.assert_called_once_with(
            [
                "mmdebstrap",
                f"--logfile={self.cwd}",
                "--architecture=amd64",
                "--verbose",
                "bookworm",
                "fake_target",
            ],
            check=True,
        )

    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    def test_bootstrap_with_extra_args(self, mock_which, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        mock_exec.return_value = (0, "")
        mock_which.return_value = "/usr/bin/mmdebstrap"
        stage = OmegaConf.create(
            {
                "target": "fake_target",
                "suite": "bookworm",
                "architecture": "amd64",
                "packages": ["ostree"],
                "setup_hooks": ["sync-in overlay/debian/ /"],
            }
        )
        bootstrap.Bootstrap(self.state, self.config, stage).run()
        mock_exec.assert_called_once_with(
            [
                "mmdebstrap",
                f"--logfile={self.cwd}",
                "--architecture=amd64",
                "--verbose",
                "--include=ostree",
                "--setup-hook=sync-in overlay/debian/ /",
                "bookworm",
                "fake_target",
            ],
            check=True,
        )
