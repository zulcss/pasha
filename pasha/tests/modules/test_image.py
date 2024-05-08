import pathlib
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha import utils
from pasha.modules import images
from pasha.tests import base


class TestImage(base.TestCase):
    def setUp(self):
        super(TestImage, self).setUp()
        self.state = mock.MagicMock()
        self.conf = OmegaConf.create(
            {"name": "fake_name", "params": {"disk": "/dev/loop0"}}
        )
        self.stage = OmegaConf.create({"name": "fake_image.img", "size": "20G"})

    @mock.patch("pasha.utils.run_command")
    def test_image_create(self, mock_exec):
        expected_calls = [
            mock.call(["truncate", "-s", "20G", "fake_image.img"]),
            mock.call(["losetup", "--partscan", "/dev/loop0", "fake_image.img"]),
        ]
        mock_exec.return_value = (0, "")
        images.RawImage(self.state, self.conf, self.stage).run()
        mock_exec.assert_has_calls(expected_calls)
