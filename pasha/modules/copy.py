"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging

from pasha.modules.base import ModuleBase
from pasha import utils


class Copy(ModuleBase):

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.rootfs = self.state.workspace.joinpath(
            f"{self.config.name}/rootfs")
        self.logging = logging.getLogger(__name__)

    def run(self):
        source = self.stage.get("source")
        cmd = ["cp", "-a", source, self.rootfs]
        utils.run_chroot_command(cmd, self.rootfs)

    def validate(self):
        pass
