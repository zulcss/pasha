"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
<<<<<<< HEAD
import os
import shlex
import shutil

from omegaconf import OmegaConf

from pasha import exceptions
from pasha.archive import unpack
=======
import shlex

>>>>>>> 9ac3dfe (add modules)
from pasha.modules.base import ModuleBase
from pasha import utils


class Command(ModuleBase):

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
        for cmd in self.stage.commands:
            utils.run_chroot_command(shlex.split(cmd), self.rootfs)
<<<<<<< HEAD
        #print(self.stage.commands)
=======

    def validate(self):
        pass
>>>>>>> 9ac3dfe (add modules)
