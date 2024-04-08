"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import shutil

from pasha.modules.base import ModuleBase
from pasha import utils


class Bootloader(ModuleBase):

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)
        self.kernel_args = self.stage.kernel_args
        self.rootfs = self.state.workspace.joinpath(
            f"{self.config.name}/rootfs")

    def run(self):
        self.logging.info("Installing bootloader")

        utils.run_chroot_command(
            ["bootctl", "install",
             "--no-variables",
             "--entry-token", "os-id"],
            self.rootfs,
            efi=self.rootfs)

        # Should be only one kernel.
        for d in self.rootfs.glob("boot/vmlinuz-*"):
            kver = d.name.removeprefix("vmlinuz-")

        cmdline = self.rootfs.joinpath("etc/kernel/cmdline")
        with open(cmdline, "w") as f:
            f.write(self.kernel_args)

        utils.run_chroot_command(
            ["kernel-install", "add", kver, f"/boot/vmlinuz-{kver}"],
            self.rootfs, efi=self.rootfs)

    def validate(self):
        pass


class BootloaderOstree(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)
        self.rootfs = self.state.workspace.joinpath(
            f"{self.config.name}/rootfs")

    def run(self):
        self.logging.info("Installing bootloader for ostree.")

        for d in self.rootfs.glob("ostree/deploy/debian/deploy/*.0"):
            repo_root = d
        utils.run_chroot_command(
            ["bootctl", "install"], repo_root, efi=self.rootfs)

        self.logging.info("Configuring bootloader.")
        shutil.copytree(self.rootfs.joinpath("boot/ostree"),
                        self.rootfs.joinpath("efi/ostree"))
        shutil.copy2(
            self.rootfs.joinpath("boot/loader/entries/ostree-1-debian.conf"),
            self.rootfs.joinpath("efi/loader/entries/ostree-0-1.conf"))

    def validate(self):
        pass
