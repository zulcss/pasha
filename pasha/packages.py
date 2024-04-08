"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import logging

from pasha import utils


class Apt(object):
    def __init__(self, state, config):
        self.state = state
        self.config = config

        self.logging = logging.getLogger(__name__)
        self.rootfs = self.state.workspace.joinpath(
            f"{self.config.name}/rootfs")

        self.env = {
            "DEBIAN_FRONTEND": "nonineractive",
            "DEBAIN_INTERACTIVE_SEEN": "True"
        }

    def clean(self):
        """Clean apt package cache."""
        self.loging.info("Running apt clean.")
        utils.run_chroot_commnad(
            ["apt", "clean"], self.rootfs, env=self.env)

    def install(self, packages):
        """Run apt package install."""
        self.logging.info("Running apt install.")
        utils.run_chroot_command(
            ["apt", "install", "-y"] + packages,
            self.rootfs, env=self.env)

    def remove(self, packages):
        """Run apt package remove."""
        self.logging.info("Removing packages.")
        utils.run_chroot_command(
            ["apt", "remove", "-y"] + packages,
            self.rootfs, env=self.env)

    def refresh(self):
        """Run apt-get update."""
        self.logging.info("Running apt update.")
        utils.run_chroot_command(
            ["apt", "update"], self.rootfs, env=self.env)

    def upgrade(self):
        """Run apt ugrade."""
        self.loging.info("Running apt upgrade.")
        utils.run_chroot_command(
            ["apt", "upgradae", "-y"], self.rootfs, env=self.env)

    def dist_upgrade(self):
        """Run apt dist-upgrade."""
        self.logging.info("Running apt full-upgrade.")
        utils.run_chroot_command(
            ["apt", "full-upgrade", "-y"], self.rootfs, env=self.env)
