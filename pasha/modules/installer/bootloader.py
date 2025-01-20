"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import shutil
import subprocess
import sys

from pasha import exceptions, target, utils
from pasha.bootloader import install_systemd_boot
from pasha.context import Context
from pasha.log import complete_step, die
from pasha.modules.base import ModuleBase
from pasha.mount import mount_disk
from pasha.ostree import ostree_ref


class Bootloader(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)

        self.kernel_args = self.context.stage.kernel_args
        self.uefi_driver = self.context.stage.get("uefi_driver", None)

        if not os.path.exists(self.context.params.disk):
            die(f"{self.context.params.disk} does not exist.")

    def run(self):
        with complete_step("Installing systemd-boot booloader"):
            with mount_disk(self.context.params.disk, self.context.root):
                install_systemd_boot(self.context)

                if self.uefi_driver == "ext4":
                    logging.info("Install ext4 file system driver for UEFI.")
                    shutil.copytree(
                        self.context.root.joinpath("usr/share/edk2/drivers"),
                        self.context.root.joinpath("efi/EFI/systemd/drivers"),
                        dirs_exist_ok=True,
                    )

                with utils.Chroot(self.context, self.context.root) as chroot:
                    logging.debug("Configuring kernel and initrd.")

                    kver = None
                    for d in self.context.root.glob("boot/vmlinuz-*"):
                        kver = d.name.removeprefix("vmlinuz-")
                    if kver is not None:
                        self.context.root.joinpath("etc/kernel").mkdir(
                            parents=True, exist_ok=True
                        )
                        cmdline = self.context.root.joinpath("etc/kernel/cmdline")
                        with open(cmdline, "w") as f:
                            f.write(self.kernel_args)

                        chroot.run(
                            ["kernel-install", "add", kver, f"/boot/vmlinuz-{kver}"]
                        )


class BootloaderOstree(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)

        self.uefi = self.context.stage.get("uefi", "systemd-boot")
        self.uefi_driver = self.context.stage.get("uefi_driver", "")

    def run(self):
        with complete_step("Installing boot loader for OSTree."):
            with mount_disk(self.context.params.disk, self.context.root):
                ref = ostree_ref(
                    self.context.root.joinpath("ostree/repo"),
                    self.context.params.branch,
                )
                repo_root = self.context.root.joinpath(
                    f"ostree/deploy/elxr/deploy/{ref}.0"
                )

                match self.uefi:
                    case "systemd-boot":
                        install_systemd_boot(self.context, ostree=True)

                        logging.info("Install ext4 file system driver for UEFI")
                        shutil.copytree(
                            os.path.join(repo_root, "usr/share/edk2/drivers"),
                            self.context.root.joinpath("efi/EFI/systemd/drivers"),
                            dirs_exist_ok=True,
                        )
                    case "grub-efi":
                        logging.info("Setting up /usr/lib/ostree-grub")
                        grub_dir = repo_root.joinpath("usr/lib/ostree-grub")
                        grub_cmds = [
                            [
                                "cp",
                                "-rf",
                                grub_dir.joinpath("grub"),
                                self.context.root.joinpath("boot"),
                            ],
                            ["rm", "-rf", self.context.root.joinpath("efi/EFI/BOOT")],
                            [
                                "cp",
                                "-rf",
                                grub_dir.joinpath("EFI"),
                                self.context.root.joinpath("efi"),
                            ],
                        ]
                        for cmd in grub_cmds:
                            subprocess.run(cmd, check=True)
                    case _:
                        die(f"{self.uefi} is not a supported type.")


class BootloaderGrub(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)
        self.mounts = self.config.params.get("mounts", None)
        self.device = self.config.params.get("image", None)
        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")

    def run(self):
        self.logging.info("Setting up grub bootloader")

        if self.device is None:
            raise exceptions.ConfigError("Disk is not specified.")
        if not os.path.exists(self.device):
            raise exceptions.ConfigError(f"{self.device} is not found.")

        try:
            with target.RunInTarget(
                image=self.config.params.image, rootfs=self.rootfs, mounts=self.mounts
            ) as chroot:
                arch = "x86_64-efi"
                if self.config.architecture == "arm64":
                    arch = "arm64-efi"
                chroot.run(["update-grub"])
                chroot.run(
                    [
                        "grub-install",
                        "--uefi-secure-boot",
                        f"--target={arch}",
                        "--no-nvram",
                        "--removable",
                    ]
                )
                chroot.run(["update-grub"])
        except RuntimeError:
            self.logging.error("Unable to run all commands. Exiting!!")
            sys.exit(1)
