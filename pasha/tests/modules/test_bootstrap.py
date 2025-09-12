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
        self.state.cache_proxy = None
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.config = OmegaConf.create({"name": "fake_name", "architecture": "amd64"})
        self.stage = OmegaConf.create(
            {"target": "fake_target", "suite": "bookworm", "architecture": "amd64"}
        )
        self.cwd = os.path.join(os.getcwd(), "mmdebstrap.log")
        self.addCleanup(self.cleanup)

    def cleanup(self):
        if os.path.exists(self.cwd):
            try:
                os.remove(self.cwd)
            except Exception as e:
                print(f"Warning: Failed to delete mmdebstrap.log: {e}")

    @mock.patch("subprocess.Popen")
    @mock.patch("shutil.which")
    def test_bootstrap(self, mock_which, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        mock_which.return_value = "/usr/bin/mmdebstrap"

        fake_proc = mock.Mock()
        fake_proc.returncode = 0
        fake_proc.stdout = [""]
        mock_exec.return_value = fake_proc

        bootstrap.Bootstrap(self.state, self.config, self.stage).run()
        mock_exec.assert_called_once_with(
            [
                "mmdebstrap",
                "--architecture=amd64",
                "--verbose",
                "bookworm",
                "fake_target",
            ],
            stdout=-1,
            stderr=-2,
            text=True,
        )

    @mock.patch("subprocess.Popen")
    @mock.patch("shutil.which")
    def test_bootstrap_with_extra_args(self, mock_which, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
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

        fake_proc = mock.Mock()
        fake_proc.stdout = [""]
        fake_proc.returncode = 0
        mock_exec.return_value = fake_proc

        bootstrap.Bootstrap(self.state, self.config, stage).run()
        mock_exec.assert_called_once_with(
            [
                "mmdebstrap",
                "--architecture=amd64",
                "--verbose",
                "--include=ostree",
                "--setup-hook=sync-in overlay/debian/ /",
                "bookworm",
                "fake_target",
            ],
            stdout=-1,
            stderr=-2,
            text=True,
        )

    @mock.patch("subprocess.Popen")
    @mock.patch("shutil.which")
    def test_bootstrap_with_cache_proxy(self, mock_which, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        mock_which.return_value = "/usr/bin/mmdebstrap"
        self.state.cache_proxy = "http://localhost:3142"

        fake_proc = mock.Mock()
        fake_proc.returncode = 0
        fake_proc.stdout = [""]
        mock_exec.return_value = fake_proc

        bootstrap.Bootstrap(self.state, self.config, self.stage).run()
        mock_exec.assert_called_once_with(
            [
                "mmdebstrap",
                "--architecture=amd64",
                "--verbose",
                '--aptopt=Acquire::http::Proxy "http://localhost:3142"',
                "bookworm",
                "fake_target",
            ],
            stdout=-1,
            stderr=-2,
            text=True,
        )
