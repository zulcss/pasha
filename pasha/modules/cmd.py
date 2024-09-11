"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import shlex

from pasha import utils
from pasha.modules.base import ModuleBase


class Command(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")

        self.logging = logging.getLogger(__name__)

    def run(self):
        for cmd in self.stage.commands:
            self.logging.info(f"Running {cmd}")
            utils.run_chroot_command(shlex.split(cmd), self.rootfs)


class ShellCommand(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)

    def run(self):
        commands = self.stage.get("commands") or []
        for cmd in commands:
            self.logging.info(f"Running {cmd}")
            utils.run_command(cmd, shell=True)
