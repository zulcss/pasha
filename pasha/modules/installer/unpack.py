"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os

from pasha.modules.base import ModuleBase
from pasha.mount import mount
from pasha import utils


class Unpack(ModuleBase):
    """Module that uses parted to create parttions."""

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)
        self.device = self.config.params.disk
        self.source = self.config.params.source
        self.rootfs = self.state.workspace.joinpath(
            f"{self.config.name}/rootfs")

    def run(self):
        self.logging.info("Unpacking source.")

        if not os.path.exists(self.source):
            raise Exception(f"Couuld not find {self.source}.")

        if not self.rootfs.exists():
            self.rootfs.mkdir(parents=True, exist_ok=True)

        self.logging.info(f"Mounting {self.device} on {self.rootfs}.")
        mount(self.device, self.rootfs)

        self.logging.info(f"Unpacking {self.source}.")
        utils.run_command(
            ["tar", "-C", self.rootfs,
             "--exclude=./dev/*",
             "-zxf", self.source, "--numeric-owner"])

    def validate(self):
        pass
