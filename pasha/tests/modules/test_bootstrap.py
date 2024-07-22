"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import pathlib
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha import utils
from pasha.modules import bootstrap
from pasha.tests import base


class TestBootstrapModule(base.TestCase):
    def setUp(self):
        super(TestBootstrapModule, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.config = OmegaConf.create({"name": "fake_name", "architecture": "amd64"})
        self.stage = OmegaConf.create({"target": "fake_target", "suite": "bookworm"})

    @mock.patch("pasha.utils.run_command")
    def test_bootstrap(self, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        mock_exec.return_value = (0, "")
        bootstrap.Bootstrap(self.state, self.config, self.stage).run()
        mock_exec.assert_called_once_with(
            [
                "/usr/bin/mmdebstrap",
                "--architecture",
                "amd64",
                "--verbose",
                "bookworm",
                "fake_target",
            ]
        )
