"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging

from pasha import utils
from pasha.modules.base import ModuleBase


class User(ModuleBase):

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")
        self.logging = logging.getLogger(__name__)

    def run(self):
        cmd = []
        username = self.stage.get("name")
        if username:
            self.logging.info(f"Adding {username}.")
            passwd = self.stage.get("passwd")
            if passwd:
                cmd += ["--password", passwd]
            groups = self.stage.get("groups")
            if groups:
                cmd += ["--groups", ",".join(groups)]

            cmd += ["--create-home"]
            cmd += ["--home", f"/home/{username}"]
            cmd += ["--shell", "/bin/bash"]

            utils.run_chroot_command(["useradd", *cmd, username], self.rootfs)

    def validate(self):
        pass
