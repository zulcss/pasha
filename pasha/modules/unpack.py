"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import shutil

from pasha import utils
from pasha.archive import unpack
from pasha.context import Context
from pasha.log import complete_step, die
from pasha.modules.base import ModuleBase


class Unpack(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)

        # parameters
        self.sources = self.context.stage.sources

    def run(self):
        with complete_step("Unpacking sources"):
            self.context.root.mkdir(parents=True, exist_ok=True)
            for source in self.sources:
                if source.startswith("http") or source.startswith("https"):
                    source = utils.fetch(source)

                if not os.path.exists(source):
                    die(f"{source} is not found.")
                unpack(source, self.context.root)
