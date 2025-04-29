"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import subprocess

from pasha.context import Context
from pasha.log import complete_step
from pasha.modules.base import ModuleBase
from pasha.mount import mount_disk


class Copy(ModuleBase):
    """Module to copy files from one destination to another."""

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)

    def run(self):
        source = self.context.stage.get("source")
        dest = self.context.stage.get("dest")
        if dest:
            dest = os.path.join(self.context.root, dest)
        else:
            dest = self.context.root

        with mount_disk(self.context.params.disk, self.context.root):
            with complete_step(f"Copying {source} to {dest}."):
                cmd = ["cp", "-rfL", source, dest]
                subprocess.run(cmd, check=True)
