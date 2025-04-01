"""
Copyright (c) 2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import os
import pathlib
import tempfile
from unittest import mock
from unittest.mock import call

import pytest
from omegaconf import OmegaConf

from pasha import utils
from pasha.modules.installer import ostree
from pasha.tests import base


class TestOstree(base.TestCase):
    def setUp(self):
        super(TestOstree, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.config = OmegaConf.create(
            {
                "name": "fake_name",
                "architecture": "amd64",
                "params": {
                    "disk": "/dev/sda",
                    "repository": "fake_path",
                    "branch": "fake_branch",
                },
            }
        )
        self.stage = OmegaConf.create({})

    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    def test_ostree_init(self, mock_which, mock_run):
        expected_calls = [
            mock.call(
                ["ostree", "init", "--repo=fake_path", "--mode=bare"],
                capture_output=True,
                check=True,
            )
        ]
        ostree.OstreeInit(self.state, self.config, self.stage).run()
        self.assertEqual(mock_run.call_args_list, expected_calls)

    @mock.patch("subprocess.run")
    @mock.patch("os.path.exists")
    @mock.patch("shutil.which")
    def test_ostree_config(self, mock_which, mock_exists, mock_run):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        rootfs = self.tempdir.joinpath("fake_name/rootfs/ostree/repo")
        expected_calls = [
            mock.call(
                ["systemd-dissect", "--mount", "--mkdir", "/dev/sda", rootfs],
                capture_output=True,
                check=True,
            ),
            mock.call(
                ["ostree", "config", "set", "--repo", "fake_repo", "fake_key", "True"],
                check=True,
            ),
            mock.call(
                ["systemd-dissect", "--umount", rootfs], capture_output=True, check=True
            ),
        ]
        mock_exists.return_value = True
        self.stage = OmegaConf.create({"config": {"fake_key": True}})
        ostree.OstreeConfig(self.state, self.config, self.stage).run()

    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    def test_ostree_commit(self, mock_which, mock_run):
        rootfs = str(self.tempdir.joinpath("fake_name/rootfs"))
        expected_calls = [
            mock.call(
                [
                    "ostree",
                    "commit",
                    rootfs,
                    "--repo=fake_path",
                    "--branch=fake_branch",
                    "--subject=Initial commit",
                ],
                capture_output=True,
                check=True,
            ),
            mock.call(["ostree", "summary", "-u", "--repo=fake_path"], check=True),
        ]
        ostree.OstreeCommit(self.state, self.config, self.stage).run()
        self.assertEqual(mock_run.call_args_list, expected_calls)
