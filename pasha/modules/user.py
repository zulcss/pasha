"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging

from pasha import utils
from pasha.context import Context
from pasha.log import complete_step
from pasha.modules.base import ModuleBase
from pasha.mount import mount_disk


class User(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)

    def run(self):
        cmd = []
        username = self.stage.get("name", None)
        if username is None:
            return
        passwd = self.stage.get("passwd")
        if passwd:
            cmd += ["--password", passwd]
        groups = self.stage.get("groups")
        if groups:
            cmd += ["--groups", ",".join(groups)]

        cmd += ["--create-home"]
        cmd += ["--home", f"/home/{username}"]
        cmd += ["--shell", "/bin/bash"]

        with complete_step(f"Adding {username}"):
            with mount_disk(self.context.params.disk, self.context):
                passwd = self.stage.get("passwd")
                groups = self.stage.get("groups")

                with utils.Chroot(self.context, self.context.root) as chroot:
                    chroot.run(["useradd", *cmd, username])
