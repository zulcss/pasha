"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import contextlib
import json
import logging
import os
import pathlib
import shutil
import subprocess
import sys

from pasha import exceptions, loop, utils
from pasha.bootloader import install_systemd_boot
from pasha.context import Context
from pasha.log import complete_step, die
from pasha.modules.base import ModuleBase
from pasha.mount import bind_mounts, mount_disk, mount_partition
from pasha.ostree import ostree_ref


class Bootloader(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)

        self.kernel_args = self.context.stage.kernel_args
        self.uefi = self.context.stage.get("uefi", "systemd-boot")
        self.uefi_driver = self.context.stage.get("uefi_driver", None)

        if not os.path.exists(self.context.params.disk):
            die(f"{self.context.params.disk} does not exist.")

    def run(self):
        with complete_step("Installing systemd-boot booloader"):
            with mount_disk(self.context.params.disk, self.context.root):
                install_systemd_boot(self.context)

                match self.uefi:
                    case "systemd-boot":
                        if self.uefi_driver == "ext4":
                            logging.info("Install ext4 file system driver for UEFI.")
                            shutil.copytree(
                                self.context.root.joinpath("usr/share/edk2/drivers"),
                                self.context.root.joinpath("efi/EFI/systemd/drivers"),
                                dirs_exist_ok=True,
                            )
                    case "grub-efi":
                        grub_dir = self.context.root.joinpath("usr/lib/ostree-grub")
                        boot_dir = self.context.root.joinpath("boot")
                        efi_dir = self.context.root.joinpath("efi")
                        try:
                            subprocess.run(
                                ["cp", "-rf", grub_dir.joinpath("grub"), boot_dir],
                                check=True,
                            )
                            subprocess.run(
                                ["rm", "-rf", efi_dir.joinpath("EFI/BOOT")], check=True
                            )
                            subprocess.run(
                                ["cp", "-rf", grub_dir.joinpath("EFI"), efi_dir],
                                check=True,
                            )
                        except subprocess.CalledProcessError as e:
                            die(f"Failed to setup grub-efi boot loader: {e}")

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

                        # Copy device tree binaries.
                        for d in self.context.root.glob("boot/ostree/elxr-*"):
                            elxr_dir = d.name.removeprefix("elxr-")

                        dtb_dir = self.context.root.joinpath(
                            f"boot/ostree/elxr-{elxr_dir}/dtb"
                        )
                        if dtb_dir.exists():
                            subprocess.run(
                                [
                                    "cp",
                                    "-rf",
                                    dtb_dir,
                                    self.context.root.joinpath("efi"),
                                ]
                            )
                    case _:
                        die(f"{self.uefi} is not a supported type.")


class BootloaderGrub(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)
        self.disk = self.context.params.disk
        if not os.path.exists(self.disk):
            die(f"{self.disk} is not found.")

    def run(self):
        with (
            complete_step("Setting up chroot target"),
            contextlib.ExitStack() as stack,
        ):
            disk = pathlib.Path(self.context.params.disk)
            if disk.suffix == ".img" or disk.suffix == ".raw":
                self.disk = stack.enter_context(loop.attach_image_loopback(self.disk))

            self.context.root.mkdir(parents=True, exist_ok=True)
            mounts = subprocess.run(
                ["systemd-dissect", "--json", "pretty", self.disk],
                check=True,
                capture_output=True,
                encoding="utf8",
            )
            mounts = json.loads(mounts.stdout)["mounts"]
            for mount in mounts:
                designator = mount["designator"]
                match designator:
                    case "root":
                        logging.debug("Mounting root")
                        self.context.root.mkdir(parents=True, exist_ok=True)
                        stack.enter_context(
                            mount_partition(
                                mount["node"], mount["fstype"], self.context.root
                            )
                        )
                    case "esp":
                        logging.debug("Mounting esp")
                        efi = self.context.root.joinpath("efi")
                        efi.mkdir(parents=True, exist_ok=True)
                        stack.enter_context(
                            mount_partition(mount["node"], mount["fstype"], efi)
                        )
            arch = "x86_64-efi"
            if self.context.config.architecture == "arm64":
                arch = "arm64-efi"
            with bind_mounts(["dev", "proc", "sys"], self.context.root):
                subprocess.run(["chroot", self.context.root, "update-grub"])
                cmd = [
                    "grub-install",
                    "--uefi-secure-boot",
                    "--efi-directory=/efi",
                    f"--target={arch}",
                    "--no-nvram",
                    "--removable",
                ]
                subprocess.run(["chroot", self.context.root] + cmd, check=True)
