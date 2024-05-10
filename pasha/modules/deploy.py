"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os

from pasha.modules.base import ModuleBase
from pasha.mount import mount, umount


class Deploy(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")

        self.logging = logging.getLogger(__name__)

    def run(self):
        self.logging.info("Running deploy.")

        if os.path.ismount(self.rootfs):
            self.logging.info("f{self.rootfs} is already mounted.")
            umount(self.rootfs)

        device = self.config.params.disk
        self.logging.info(f"Mounting {device}.")
        self.rootfs.mkdir(parents=True, exist_ok=True)
        mount(device, self.rootfs)

    def validate(self):
        pass


class Undeploy(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")

        self.logging = logging.getLogger(__name__)

    def run(self):
        self.logging.info("Running undeploy.")
        device = self.config.params.disk
        self.logging.info(f"Unmounting {device}.")
        umount(self.rootfs)

    def validate(self):
        pass
