"""
Copyright (c) 2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import os
import pathlib
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha.modules.security import trivy
from pasha.tests import base


class TestTrivy(base.TestCase):
    def setUp(self):
        super(TestTrivy, self).setUp()
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
        self.stage = OmegaConf.create([])

    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    def test_run_trivy(self, mock_shutil, mock_exec):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        cwd = pathlib.Path(os.getcwd()).resolve()
        expected_calls = [
            mock.call(["systemctl", "--version"], capture_output=True, text=True),
            mock.call(
                ["systemd-dissect", "--mount", "--mkdir", "/dev/sda", rootfs],
                capture_output=True,
                check=True,
                env={},
            ),
            mock.call(
                [
                    "trivy",
                    "rootfs",
                    "--output",
                    cwd.joinpath("cve_scan_result.txt"),
                    "--scanners",
                    "vuln",
                    rootfs,
                ],
                check=True,
            ),
            mock.call(
                ["systemd-dissect", "--umount", rootfs], capture_output=True, check=True
            ),
        ]
        rootfs.mkdir(parents=True, exist_ok=True)
        trivy.TrivyVulnScan(self.state, self.config, self.stage).run()
        self.assertEqual(mock_exec.call_args_list, expected_calls)
