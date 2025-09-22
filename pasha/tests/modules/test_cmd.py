"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

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
        self.config = OmegaConf.create(
            {
                "name": "fake_name",
                "architecture": "amd64",
                "params": {
                    "disk": "/dev/sda",
                },
            }
        )
        self.stage = OmegaConf.create({"commands": ["pwd", "ls -lh"]})

    @mock.patch("subprocess.run")
    def test_run_shell(self, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        expected_calls = [
            mock.call(
                ["systemd-dissect", "--mount", "--mkdir", "/dev/sda", rootfs],
                check=True,
                capture_output=True,
            ),
            mock.call("pwd", shell=True, cwd=None),
            mock.call("ls -lh", shell=True, cwd=None),
            mock.call(
                ["systemd-dissect", "--umount", rootfs], capture_output=True, check=True
            ),
        ]
        rootfs.mkdir(parents=True, exist_ok=True)
        cmd.ShellCommand(self.state, self.config, self.stage).run()
        self.assertEqual(mock_exec.call_args_list, expected_calls)

    @mock.patch("subprocess.run")
    def test_run_shell_from_root_dir(self, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        stage_with_root_dir = OmegaConf.create(
            {"commands": ["pwd", "ls -lh"], "from_root_dir": True}
        )
        expected_calls = [
            mock.call(
                ["systemd-dissect", "--mount", "--mkdir", "/dev/sda", rootfs],
                check=True,
                capture_output=True,
            ),
            mock.call("pwd", shell=True, cwd=rootfs),
            mock.call("ls -lh", shell=True, cwd=rootfs),
            mock.call(
                ["systemd-dissect", "--umount", rootfs], capture_output=True, check=True
            ),
        ]
        rootfs.mkdir(parents=True, exist_ok=True)
        cmd.ShellCommand(self.state, self.config, stage_with_root_dir).run()
        self.assertEqual(mock_exec.call_args_list, expected_calls)
