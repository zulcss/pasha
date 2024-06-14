"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os.path

from pasha import utils
from pasha.modules.base import ModuleBase


class Copy(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")
        self.logging = logging.getLogger(__name__)

    def run(self):
        source = self.stage.get("source")
        dest = self.stage.get("dest")
        if dest:
            dest = os.path.join(self.rootfs, dest)
        else:
            dest = self.rootfs

        cmd = ["cp", "-rfL", source, dest]
        utils.run_command(cmd)
