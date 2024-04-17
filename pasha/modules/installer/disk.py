"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import shlex
import shutil

from pasha import exceptions, utils
from pasha.modules.base import ModuleBase


class Parted(ModuleBase):
    """Module that uses parted to create partitions."""

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)
        self.device = self.config.params.disk
        self.slices = self.stage.slices

    def run(self):
        self.logging.info("Running parted.")

        if not os.path.exists(self.device):
            raise exceptions.ConfigError(f"{self.device} does not exist.")

        self.logging.info("Creating gpt disk label.")
        utils.run_command(["parted", self.device, "--script", "mklabel", "gpt"])

        self.logging.info("Creating partitions.")
        for index, part in enumerate(self.slices, start=1):
            self.logging.info(f"Creating partition {index}: {part.name}")
            utils.run_command(
                [
                    "parted",
                    "-a",
                    "optimal",
                    "-s",
                    self.device,
                    "--",
                    "mkpart",
                    part.name,
                    part.start,
                    part.end,
                ]
            )
            if len(part.flags) != 0:
                for flag in part.flags:
                    utils.run_command(
                        [
                            "parted",
                            "-a",
                            "optimal",
                            "-s",
                            self.device,
                            "--",
                            "set",
                            str(index),
                            flag,
                            "on",
                        ]
                    )
            if part.id:
                cmd = f"sfdisk --part-type {self.device} {index} {part.id}"
                utils.run_command(shlex.split(cmd))

    def validate(self):
        pass


class Reparted(ModuleBase):
    """Module that uses systemd-repart to create partitions."""

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)

    def run(self):
        self.logging.info("Running systemd-repoart")

        repart = shutil.which("systemd-repart")
        if repart is None:
            raise Exception("systemd-repoart binary not found.")

        device = self.config.params.disk
        if device:
            if os.path.exists(device):
                self.logging.info(f"Found {device} from a previous run.")
                os.unlink(device)
            size = self.stage.get("size")
            if size is None:
                raise Exception("disk size is not specified.")
            definitions = self.stage.get("definitions")
            if definitions is None:
                raise Exception("disk definitions not specified.")

            self.logging.info(f"Creating {device}.")
            utils.run_command(
                [
                    repart,
                    "--definitions",
                    str(definitions),
                    "--empty=create",
                    "--size",
                    size,
                    "--dry-run=no",
                    "--discard=no",
                    "--no-pager",
                    str(device),
                ]
            )
        else:
            raise Exception("Disk image is not specified.")

    def validate(self):
        pass


class Filesystem(ModuleBase):
    """Module that create filesystems on partitions."""

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)

    def run(self):
        self.logging.info("Running filesystems.")

        device = self.config.params.disk
        if device:
            filesystems = self.stage.get("filesystems")
            if filesystems:
                for index, part in enumerate(filesystems, start=1):
                    fs = self._get_partition_device(index, device)
                    if os.path.exists(fs):
                        self._mkfs(fs, part.fs, part.label, part.name)
        else:
            raise Exception("Disk image is not specified.")

    def validate(self):
        pass

    def _mkfs(self, fs, fs_type, label, name):
        self.logging.info(f"Formatting filesystems for {name}.")

        if fs_type == "vfat":
            # vfat is a special case
            utils.run_command(["mkfs.vfat", "-F", "32", "-n", label, fs])
        else:
            utils.run_command(["mkfs", "-F", "-t", fs_type, "-L", label, fs])

    def _get_partition_device(self, number, device):
        """Get the partition device."""
        suffix = "p"
        # Check partition naming first: if used 'by-id'i naming convention
        if "/disk/by-id" in device:
            suffix = "-part"

        # If the image device has a digit as the last character, the partition
        # suffix is p<number> else it's just <number>
        last = device[len(device) - 1]
        if last >= "0" and last <= "9":
            return "%s%s%d" % (device, suffix, number)
        else:
            return "%s%d" % (device, number)
