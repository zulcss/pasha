"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import shutil
import tempfile

from pasha import utils
from pasha.archive import unpack
from pasha.modules.base import ModuleBase


class Container(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)

    def run(self):
        source = self.config.params.get("source", None)
        if source is None:
            raise ValueError(f"Container source not specified: '{source}'")
        if not os.path.exists(source):
            raise Exception(f"'{source}' does not exist")

        image = self.stage.get("image", None)
        if image is None:
            raise ValueError(f"Container image not specified: '{image}'")
        image_name = image.split(":")[0]

        if not shutil.which("umoci"):
            raise Exception("umoci is not installed.")

        if os.path.exists(image_name):
            shutil.rmtree(image_name)

        utils.run_command(f"umoci init --layout {image_name}", shell=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            archive_dir = os.path.join(tmpdir, "root")
            os.makedirs(archive_dir)
            unpack(source, archive_dir)

            utils.run_command(f"umoci new --image {image_name}", shell=True)
            utils.run_command(
                f"umoci insert --image {image} {archive_dir} /", shell=True
            )
