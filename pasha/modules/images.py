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
        self.disk = self.config.params.get("disk")
        self.logging.info(f"Creating {self.image} on {self.disk}.")

        if os.path.exists(self.image):
            self.logging.info(f"Found existing {self.image}. Removing.")
            os.unlink(self.image)

        cmd = ["truncate", "-s", self.size, self.image]
        ret, _ = utils.run_command(cmd)
        if ret != 0:
            raise Exception(f"Failed to create {self.image}.")
        self.logging.info(f"Attaching {self.image} to {self.disk}")
        cmd = ["losetup", "--partscan", self.disk, self.image]
        ret, _ = utils.run_command(cmd)
        if ret != 0:
            raise Exception(f"Failed to attach {self.image} to {self.disk}.")

    def validate(self):
        pass


class CompressImage(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.logging = logging.getLogger(__name__)

    def run(self):
        self.image = self.stage.get("name")
        self.compressor = self.stage.get("compression", "xz")
        self.logging.info(f"Compress {self.image}.")

        if not os.path.exists(self.image):
            self.logging.info(f"{self.image} not found")
            sys.exit(1)

        compress(self.image, compressor=self.compressor)

    def validate(self):
        pass
