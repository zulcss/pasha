"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import subprocess
import sys

from pasha import exceptions, utils
from pasha.archive import compress
from pasha.context import Context
from pasha.log import complete_step, die
from pasha.modules.base import ModuleBase


class RawImage(ModuleBase):
    """Create a raw disk image."""

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)

        self.size = self.context.stage.get("size", None)
        if self.size is None:
            """Size of image, Valid unit size M and G (powers of 1024)."""
            raise exceptions.ConfigError("Disk size is not specified.")

        # FIXME(chuck) - Attach timestamp to image.
        self.image = self.context.stage.get("name", None)
        if self.image is None:
            """Name of image."""
            raise exceptions.ConfigError("Image name is not specified.")

    def run(self):
        with complete_step(f"Creating {self.image}"):
            if os.path.exists(self.image):
                logging.debug(f"Found existing {self.image}. Removing.")
                os.unlink(self.image)
        try:
            subprocess.run(
                ["truncate", "-s", self.size, self.image],
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            die("Failed to create disk image: " + e.stderr.decode("utf-8").strip())
