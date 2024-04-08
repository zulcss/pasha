"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
<<<<<<< HEAD
import shutil

from omegaconf import OmegaConf

from pasha import exceptions
from pasha.archive import unpack
from pasha.mount import mount
from pasha.mount import umount
from pasha.modules.base import ModuleBase
=======

from pasha.modules.base import ModuleBase
from pasha.mount import mount
from pasha.mount import umount
>>>>>>> 9ac3dfe (add modules)


class Deploy(ModuleBase):

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.rootfs = self.state.workspace.joinpath(
<<<<<<< HEAD
                f"{self.config.name}/rootfs")
=======
            f"{self.config.name}/rootfs")
>>>>>>> 9ac3dfe (add modules)

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

<<<<<<< HEAD
=======
    def validate(self):
        pass


>>>>>>> 9ac3dfe (add modules)
class Undeploy(ModuleBase):

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.rootfs = self.state.workspace.joinpath(
<<<<<<< HEAD
                f"{self.config.name}/rootfs")
=======
            f"{self.config.name}/rootfs")
>>>>>>> 9ac3dfe (add modules)

        self.logging = logging.getLogger(__name__)

    def run(self):
        self.logging.info("Running undeploy.")
        device = self.config.params.disk
        self.logging.info(f"UnMounting {device}.")
        umount(self.rootfs)

<<<<<<< HEAD

=======
    def validate(self):
        pass
>>>>>>> 9ac3dfe (add modules)
