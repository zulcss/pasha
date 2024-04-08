"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
<<<<<<< HEAD
import os
import shutil

from omegaconf import OmegaConf

from pasha import exceptions
from pasha import utils
from pasha.modules.base import ModuleBase
=======

from pasha.modules.base import ModuleBase
from pasha.packages import Apt
>>>>>>> 9ac3dfe (add modules)


class AptBase(ModuleBase):

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
<<<<<<< HEAD
        self.rootfs = self.state.workspace.joinpath(
                f"{self.config.name}/rootfs")

        self.logging = logging.getLogger(__name__)
        self.env = {
            "DEBIAN_FRONTEND": "nonineractive",
            "DEBAIN_INTERACTIVE_SEEN": "rrue"
        }
=======

        self.logging = logging.getLogger(__name__)
        self.apt = Apt(self.state, self.config)
>>>>>>> 9ac3dfe (add modules)

    def run(self):
        pass

<<<<<<< HEAD
class AptUpdate(AptBase):
    def run(self):
        self.logging.info("Running apt update.")
        utils.run_chroot_command(["apt", "update"], self.rootfs, env=self.env)

class AptInstall(AptBase):
    def run(self):
        self.logging.info("Running apt install.")
        cmd = ["apt", "install", "-y"] + self.stage.packages
        utils.run_chroot_command(cmd, self.rootfs, env=self.env)
=======
    def validate(self):
        pass


class AptClean(AptBase):
    def run(self):
        self.apt.clean()

    def validate(self):
        pass


class AptRemove(AptBase):
    def run(self):
        self.apt.remove(self.stage.packages)


class AptUpdate(AptBase):
    def run(self):
        self.apt.refresh()

    def validate(self):
        pass


class AptUpgrade(AptBase):
    def run(self):
        self.apt.upgrade()

    def validate(self):
        pass


class AptDistUpgrade(AptBase):
    def run(self):
        self.apt.dist_upgrade()

    def validate(self):
        pass


class AptInstall(AptBase):
    def run(self):
        self.apt.install(self.stage.packages)

    def validate(self):
        pass
>>>>>>> e727d14 (fix pep8)
>>>>>>> 9ac3dfe (add modules)
