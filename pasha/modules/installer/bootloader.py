"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import shutil

from pasha import utils
from pasha.modules.base import ModuleBase


class Bootloader(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)
        self.kernel_args = self.stage.kernel_args
        self.uefi_driver = self.stage.get("uefi_driver", "")
        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")

    def run(self):
        self.logging.info("Installing bootloader")

        utils.run_chroot_command(
            ["bootctl", "install", "--no-variables", "--entry-token", "os-id"],
            self.rootfs,
            efi=self.rootfs,
            boot=self.rootfs,
        )

        # Set timeout for boot menu
        with open(self.rootfs.joinpath("efi/loader/loader.conf"), "w") as f:
            f.write("# Auto-genernated by ruck\n")
            f.write("timeout 3\n")

        # Install ext4 file system driver for UEFI
        if self.uefi_driver == "ext4":
            self.logging.info("Install ext4 file system driver for UEFI")
            shutil.copytree(
                self.rootfs.joinpath("usr/share/edk2/drivers"),
                self.rootfs.joinpath("efi/EFI/systemd/drivers"),
                dirs_exist_ok=True,
            )

        # Should be only one kernel.
        for d in self.rootfs.glob("boot/vmlinuz-*"):
            kver = d.name.removeprefix("vmlinuz-")

        cmdline = self.rootfs.joinpath("etc/kernel/cmdline")
        with open(cmdline, "w") as f:
            f.write(self.kernel_args)

        utils.run_chroot_command(
            ["kernel-install", "add", kver, f"/boot/vmlinuz-{kver}"],
            self.rootfs,
            efi=self.rootfs,
            boot=self.rootfs,
        )

    def validate(self):
        pass


class BootloaderOstree(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)
        self.uefi_driver = self.stage.get("uefi_driver", "")
        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")

    def run(self):
        self.logging.info("Installing bootloader for ostree.")

        for d in self.rootfs.glob("ostree/deploy/debian/deploy/*.0"):
            repo_root = d
        utils.run_chroot_command(
            [
                "bootctl",
                "install",
                "--boot-path",
                "/boot",
                "--no-variables",
                "--entry-token",
                "os-id",
            ],
            repo_root,
            efi=self.rootfs,
            boot=self.rootfs,
        )

        self.logging.info("Configuring bootloader.")
        # Set timeout for boot menu
        with open(self.rootfs.joinpath("efi/loader/loader.conf"), "w") as f:
            f.write("# Auto-genernated by ruck\n")
            f.write("timeout 3\n")

        # Install ext4 file system driver for UEFI
        if self.uefi_driver == "ext4":
            self.logging.info("Install ext4 file system driver for UEFI")
            shutil.copytree(
                os.path.join(repo_root, "usr/share/edk2/drivers"),
                self.rootfs.joinpath("efi/EFI/systemd/drivers"),
                dirs_exist_ok=True,
            )

    def validate(self):
        pass
