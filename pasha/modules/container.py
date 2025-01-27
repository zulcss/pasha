"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import shutil
import subprocess

from pasha.archive import unpack
from pasha.context import Context
from pasha.modules.base import ModuleBase


class Container(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)
        self.source = self.context.config.params.source
        self.image = self.context.stage.image

        if not shutil.which("umoci"):
            raise Exception("umoci is not installed.")

        if not os.path.exists(self.source):
            raise Exception(f"'{self.source}' does not exist")

    def run(self):
        image_name = self.image.split(":")[0]

        if os.path.exists(image_name):
            shutil.rmtree(image_name)

        subprocess.run(f"umoci init --layout {image_name}", shell=True)

        unpack(self.source, self.context.root)

        subprocess.run(f"umoci new --image {image_name}", shell=True)
        subprocess.run(
            f"umoci insert --image {self.image} {self.context.root} /", shell=True
        )
