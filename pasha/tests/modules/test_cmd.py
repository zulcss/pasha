"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import pathlib
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha.modules import cmd
from pasha.tests import base


class TestShellCommand(base.TestCase):
    def setUp(self):
        super(TestShellCommand, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.conf = OmegaConf.create({"name": "fake_name"})
        self.stage = OmegaConf.create({"commands": ["pwd", "ls -lh"]})

    @mock.patch("pasha.utils.run_command")
    def test_run_shell(self, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs.mkdir(parents=True, exist_ok=True)
        mock_exec.return_value = (0, "")
        cmd.ShellCommand(self.state, self.conf, {}).run()
