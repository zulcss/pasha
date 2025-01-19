"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import shutil

from pasha.archive import unpack
from pasha.context import Context
from pasha.log import complete_step, die
from pasha.modules.base import ModuleBase
from pasha.mount import mount_disk


class Unpack(ModuleBase):
    """Unpack a tarball to a disk."""

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)

        if not os.path.exists(self.context.params.source):
            die(f"{self.context.params.source} is not found.")

        if not os.path.exists(self.context.params.disk):
            die(f"{self.context.params.disk} is not found.")

    def run(self):
        with complete_step(f"Unpacking {self.context.params.source}"):
            with mount_disk(self.context.params.disk, self.context.root):
                unpack(self.context.params.source, self.context.root)
