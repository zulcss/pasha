"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import shlex
import subprocess

from pasha import utils
from pasha.context import Context
from pasha.log import complete_step, die
from pasha.modules.base import ModuleBase
from pasha.mount import mount_disk


class Command(ModuleBase):
    """Run a shell command in the chroot."""

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)

    def run(self):
        with mount_disk(self.context.params.disk, self.context.root):
            for cmd in self.context.stage.commands:
                with complete_step(f"Running {cmd}"):
                    with user.Chroot(self.context, self.context.root) as chroot:
                        chroot.run(shlex.split(cmd))


class ShellCommand(ModuleBase):
    """Run a command on the mounted disk."""

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)

    def run(self):
        commands = self.context.stage.get("commands") or []
        with mount_disk(self.context.params.disk, self.context.root):
            for cmd in commands:
                with complete_step(f"Running {cmd}"):
                    subprocess.run(cmd, shell=True)
