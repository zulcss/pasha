"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging

from pasha.modules.base import ModuleBase
from pasha.packages import Apt


class AptBase(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.logging = logging.getLogger(__name__)
        self.apt = Apt(self.state, self.config)

        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")

    def run(self):
        pass

    def validate(self):
        pass


class AptClean(AptBase):
    def run(self):
        self.logging.info("Cleaning package database.")
        if not self.rootfs.exists():
            raise Exception("Unable to find rootfs.")

        self.apt.clean()

    def validate(self):
        pass


class AptRemove(AptBase):
    def run(self):
        self.logging.info("Removing packages.")
        if not self.rootfs.exists():
            raise Exception("Unable to find rootfs.")
        packages = self.stage.get("packages")
        if packages is None:
            raise Exception(f"Unable to remove {packages}")
        self.apt.remove(packages)

    def validate(self):
        pass


class AptUpdate(AptBase):
    def run(self):
        self.logging.info("Updating package database")
        if not self.rootfs.exists():
            raise Exception("Unable to find rootfs.")
        self.apt.refresh()

    def validate(self):
        pass


class AptUpgrade(AptBase):
    def run(self):
        self.logging.info("Upgrading installed packages.")
        if not self.rootfs.exists():
            raise Exception("Unable to find rootfs.")

        self.apt.upgrade()

    def validate(self):
        pass


class AptDistUpgrade(AptBase):
    def run(self):
        self.logging.info("Running apt-get dist-upgrade.")
        if not self.rootfs.exists():
            raise Exception("Unable to find rootfs.")
        self.apt.dist_upgrade()

    def validate(self):
        pass


class AptInstall(AptBase):
    def run(self):
        self.logging.info("Installing packages.")
        if not self.rootfs.exists():
            raise Exception("Unable to find rootfs.")

        packages = self.stage.get("packages")
        if packages is None:
            raise Exception("No package specified.")
        self.apt.install(self.stage.packages)

    def validate(self):
        pass
