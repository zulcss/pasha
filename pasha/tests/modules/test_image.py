"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

from unittest import mock

import pytest
from omegaconf import OmegaConf

from pasha import exceptions, utils
from pasha.modules.images.compress import CompressImage
from pasha.modules.images.raw import RawImage
from pasha.tests import base


class TestImage(base.TestCase):
    def setUp(self):
        super(TestImage, self).setUp()
        self.state = mock.MagicMock()
        self.conf = OmegaConf.create(
            {"name": "fake_name", "params": {"disk": "/dev/loop0"}}
        )
        self.stage = OmegaConf.create({"name": "fake_image.img", "size": "20G"})

    @mock.patch("subprocess.run")
    @mock.patch("os.path.exists")
    @mock.patch("os.unlink")
    def test_image_create(self, mock_unlink, mock_os_path, mock_exec):
        expected_calls = [
            mock.call(
                ["truncate", "-s", "20G", "fake_image.img"],
                check=True,
                capture_output=True,
            ),
        ]
        mock_exec.return_value = (0, "")
        mock_os_path.return_value = True
        RawImage(self.state, self.conf, self.stage).run()
        mock_exec.assert_has_calls(expected_calls)
        mock_unlink.assert_called_once_with("fake_image.img")

    def test_image_create_without_image_name(self):
        stage = OmegaConf.create({"size": "20G"})
        with pytest.raises(exceptions.ConfigError):
            RawImage(self.state, self.conf, stage).run()

    def test_image_create_without_image_size(self):
        stage = OmegaConf.create({"name": "foo"})
        with pytest.raises(exceptions.ConfigError):
            RawImage(self.state, self.conf, stage).run()


class TestImageCompress(base.TestCase):
    def setUp(self):
        super(TestImageCompress, self).setUp()
        self.state = mock.MagicMock()
        self.conf = OmegaConf.create(
            {
                "name": "fake_name",
                "params": {"disk": "/dev/loop0", "image": "fake_image"},
            }
        )
        self.stage = OmegaConf.create({"name": "fake_image.img", "size": "20G"})

    @mock.patch("pasha.archive.compress")
    @mock.patch("os.path.exists")
    @mock.patch("subprocess.run")
    def test_image_compress(self, mock_exec, mock_os_path, mock_compress):
        stage = OmegaConf.create({"name": "fake_image"})
        mock_os_path.return_value = True
        CompressImage(self.state, self.conf, stage).run()
        mock_os_path.assert_called_with("fake_image")

    @mock.patch("sys.exit")
    def test_image_compress_without_name(self, mock_sys):
        stage = OmegaConf.create({"compression": "zstd"})
        CompressImage(self.state, self.conf, stage).run()
        mock_sys.assert_called()
