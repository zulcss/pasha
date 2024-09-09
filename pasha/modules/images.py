"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import sys

from pasha import exceptions, utils
from pasha.archive import compress
from pasha.modules.base import ModuleBase


class RawImage(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.logging = logging.getLogger(__name__)

    def run(self):
        self.size = self.stage.get("size", None)
        if self.size is None:
            raise exceptions.ConfigError("Disk size is not specified.")
        self.disk = self.stage.get("name", None)
        if self.disk is None:
            raise exceptions.ConfigError("Disk is not specified.")
        self.logging.info(f"Creating {self.disk}")

        if os.path.exists(self.disk):
            self.logging.info(f"Found existing {self.disk}. Removing.")
            os.unlink(self.disk)

        utils.run_command(["truncate", "-s", self.size, self.disk])


class CompressImage(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.logging = logging.getLogger(__name__)

    def run(self):
        self.image = self.stage.get("name", None)
        if self.image is None:
            raise exceptions.ConfigError("Image to compress is not specified.")
        self.compressor = self.stage.get("compression", "zstd")
        self.logging.info(f"Compress {self.image}.")

        if not os.path.exists(self.image):
            self.logging.info(f"{self.image} not found")
            sys.exit(1)

        compress(self.image, compressor=self.compressor)
