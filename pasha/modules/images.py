"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os

from pasha import utils
from pasha.archive import compress
from pasha.modules.base import ModuleBase


class RawImage(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.logging = logging.getLogger(__name__)

    def run(self):
        self.image = self.stage.get("name")
        self.size = self.stage.get("size")
        self.logging.info(f"Creating {self.image}")

        if os.path.exists(self.image):
            self.logging.info(f"Found existing {self.image}. Removing.")
            os.unlink(self.image)

        utils.run_command(["truncate", "-s", self.size, self.image])


class CompressImage(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.logging = logging.getLogger(__name__)

    def run(self):
        self.image = self.stage.get("name")
        self.compressor = self.stage.get("compression", "zstd")
        self.logging.info(f"Compress {self.image}.")

        if not os.path.exists(self.image):
            self.logging.info(f"{self.image} not found")
            sys.exit(1)

        compress(self.image, compressor=self.compressor)
