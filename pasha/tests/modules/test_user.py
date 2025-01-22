"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import pathlib
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha.modules import user
from pasha.tests import base


class TestUnDeploy(base.TestCase):
    def setUp(self):
        super(TestUnDeploy, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.conf = OmegaConf.create({"name": "fake_name"})
        self.stage = OmegaConf.create(
            {"user": "fake_user", "passwd": "fake_pass", "groups": ["sudo"]}
        )

    @mock.patch("pasha.utils.Chroot.run")
    def test_create_user(self, mock_run):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        expected_calls = []
        rootfs.mkdir(parents=True, exist_ok=True)
        user.User(self.state, self.conf, {}).run()
