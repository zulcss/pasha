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

    def run(self):
        pass

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

    def validate(self):
        pass


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
