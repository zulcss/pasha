"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import os

from pasha import utils


class Apt(object):
    def __init__(self, state, config):
        self.state = state
        self.config = config

        self.logging = logging.getLogger(__name__)
        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")

    def clean(self):
        """Clean apt-get package cache."""
        self.logging.info("Running apt-get clean.")
        ret, _ = utils.run_chroot_command(["apt-get", "clean"], self.rootfs)
        if ret != 0:
            raise Exception(f"Failed to run apt-get clean.")

    def install(self, packages):
        """Run apt-get package install."""
        self.logging.info("Running apt-get install.")
        env = os.environ.copy()
        env["DEBIAN_FRONTEND"] = "noninteractive"

        for package in packages:
            self.logging.info(f"Installing {package}.")
            ret, output = utils.run_chroot_command(
                ["apt-get", "install", "-y", package], self.rootfs, env=env
            )
            if ret != 0:
                raise Exception(f"Failed to apt-get install {package}: {output}")

    def remove(self, packages):
        """Remove a package"""
        self.logging.info("Removing packages.")
        env = os.environ.copy()
        env["DEBIAN_FRONTEND"] = "noninteractive"
        for package in packages:
            self.logging.info(f"Removing {package}.")
            ret, output = utils.run_chroot_command(
                ["apt-get", "remove", "-y", packages], self.rootfs, env=env
            )
            if ret != 0:
                raise Exception(f"Failed to apt-get remove {package}: {output}")

    def refresh(self):
        """Run apt-get update."""
        self.logging.info("Running apt-get update.")
        ret, output = utils.run_chroot_command(["apt-get", "update"], self.rootfs)
        if ret != 0:
            raise Exception(f"Failed to run apt-get update: {output}")

    def upgrade(self):
        """Run apt-get upgrade."""
        self.logging.info("Running apt-get upgrade.")
        ret, output = utils.run_chroot_command(
            ["apt-get", "upgrade", "-y"], self.rootfs
        )
        if ret != 0:
            raise Exception(f"Failed to run apt-get upgrade: {output}")

    def dist_upgrade(self):
        """Run apt-get dist-upgrade."""
        self.logging.info("Running apt full-upgrade.")
        ret, output = utils.run_chroot_command(
            ["apt-get", "dist-upgrade", "-y"], self.rootfs
        )
        if ret != 0:
            raise Exception(f"Failed to run apt-get dist-upgrade: {output}")
