"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import pathlib
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha.modules import oci
from pasha.tests import base


class TestContainerBuildModule(base.TestCase):
    def setUp(self):
        super(TestContainerBuildModule, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.config = OmegaConf.create(
            {
                "name": "fake_name",
                "architecture": "amd64",
                "params": {"source": "rootfs.tar.gz"},
            }
        )
        self.stage = OmegaConf.create({"image": "fake_image:latest"})

    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    @mock.patch("os.path.exists")
    @mock.patch("shutil.rmtree")
    def test_container_build(self, mock_tree, mock_path, mock_which, mock_run):
        oci.ContainerCreate(self.state, self.config, self.stage).run()
        bundle_dir = self.state.workspace.joinpath("fake_name/fake_image-unpacked")
        rootfs = bundle_dir.joinpath("rootfs")
        expected_calls = [
            mock.call(["umoci", "init", "--layout", "fake_image"]),
            mock.call(["umoci", "new", "--image", "fake_image:latest"]),
            mock.call(["umoci", "unpack", "--image", "fake_image:latest", bundle_dir]),
            mock.call(
                [
                    "tar",
                    "-C",
                    rootfs,
                    "--exclude=./dev/*",
                    "-zxf",
                    "rootfs.tar.gz",
                    "--numeric-owner",
                ],
                check=True,
                capture_output=True,
            ),
            mock.call(["umoci", "repack", "--image", "fake_image:latest", bundle_dir]),
        ]
        self.assertEqual(mock_run.call_args_list, expected_calls)
