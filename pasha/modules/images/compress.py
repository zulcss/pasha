"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os

from pasha.archive import compress
from pasha.context import Context
from pasha.log import complete_step, die
from pasha.modules.base import ModuleBase


class CompressImage(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)
        self.compressor = self.context.stage.get("compression", "zstd")

    def run(self):
        with complete_step(f"Compressing {self.context.params.disk}."):
            if not os.path.exists(self.context.params.disk):
                die(f"{self.context.params.disk} not found")

            compress(self.context.params.disk, compressor=self.compressor)
