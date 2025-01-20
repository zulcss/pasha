"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging

from rich.console import Console

from pasha.context import Context
from pasha.log import complete_step
from pasha.modules.base import ModuleBase
from pasha.mount import mount_disk
from pasha.packages import run_apt_command

console = Console()


class AptBase(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)

    def run(self):
        pass


class AptRemove(AptBase):
    def run(self):
        with complete_step("Removing packages"):
            with console.status("Removing packages."):
                with mount_disk(self.context.params.disk, self.context.root):
                    run_apt_command(
                        "remove", self.context, packages=self.context.stage.packages
                    )


class AptUpdate(AptBase):
    def run(self):
        with console.status("Updating package database"):
            with mount_disk(self.context.params.disk, self.context.root):
                run_apt_command("update", self.context)


class AptInstall(AptBase):
    def run(self):
        with complete_step("Installing packages"):
            with mount_disk(self.context.params.disk, self.context.root):
                with console.status("Updating apt cache."):
                    run_apt_command("update", self.context)

                with console.status("Installing packages."):
                    run_apt_command(
                        "install", self.context, packages=self.context.stage.packages
                    )
