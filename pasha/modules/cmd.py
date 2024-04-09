"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import shlex

from pasha.modules.base import ModuleBase
from pasha import utils


class Command(ModuleBase):

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.rootfs = self.state.workspace.joinpath(
            f"{self.config.name}/rootfs")

        self.logging = logging.getLogger(__name__)

    def run(self):
        for cmd in self.stage.commands:
            utils.run_chroot_command(shlex.split(cmd), self.rootfs)

    def validate(self):
        pass
