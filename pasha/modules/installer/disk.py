"""
Copyright (c) 2024,2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import contextlib
import logging
import os
import pathlib
import shlex
import shutil
import subprocess

import click

from pasha.context import Context
from pasha.log import complete_step, die
from pasha.loop import attach_image_loopback
from pasha.modules.base import ModuleBase


def show_disk(disk):
    """Display the results of the parted command."""
    try:
        logging.info("\nDisk layout result\n")
        subprocess.run(["parted", disk, "print"], check=True)
    except subprocess.CalledProcessError as e:
        die(f"Failed to display disk:" + e.stderr.decode("utf-8").strip())


class Parted(ModuleBase):
    """Module that uses parted to create partitions."""

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        if not shutil.which("parted"):
            die(
                "Parted is not installed",
                hint="As root run 'apt-get install -y parted' to install parted.",
            )

        if not shutil.which("sfdisk"):
            die(
                "sfdisk is not installed.",
                hint="As root run 'apt-get install -y fdisk' to install sfdisk.",
            )

        self.context = Context(self.state, self.config, self.stage)
        self.erase = self.context.stage.get("noerase", False)
        self.disk = self.context.params.disk

        if not os.path.exists(self.disk):
            die(f"{self.disk} does not exist.")

    def run(self):
        with complete_step("Creating partition table"):
            if self.erase:
                try:
                    subprocess.run(
                        ["wipefs", "-f", "-a", self.disk],
                        capture_output=True,
                        check=True,
                    )
                except subprocess.CalledProcessError as e:
                    die(f"Failed to run wipefs:" + e.stderr.decode("utf-8").strip())

            commands = ["mklabel", "gpt"]
            for index, part in enumerate(self.context.stage.slices, start=1):
                logging.info(f"Creating partition {index}: {part['name']}")
                commands += ["mkpart", part["name"], part["start"], part["end"]]
                if len(part["flags"]) != 0:
                    for flag in part["flags"]:
                        commands += ["set", str(index), flag, "on"]

            self.run_parted(commands)

            """Set the UUID for partition so can mount the block device
               later via systemd-dissect."""
            for index, part in enumerate(self.context.stage.slices, start=1):
                id = part["id"]
                if id:
                    try:
                        cmd = f"sfdisk --part-type {self.disk} {index} {id}"
                        subprocess.run(
                            shlex.split(cmd),
                            capture_output=True,
                            check=True,
                        )
                    except subprocess.CalledProcessError as e:
                        die(f"Failed to run sfdisk:" + e.stderr.decode("utf-8").strip())

            show_disk(self.disk)

    def run_parted(self, commands):
        try:
            logging.info(f"Running parted on {self.disk}.")
            subprocess.run(
                ["parted", "-a", "optimal", "-s", self.disk, "--"] + commands,
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            die(f"Failed to run parted: " + e.stderr.decode("utf-8").strip())


class Filesystem(ModuleBase):
    """Module that create filesystems on partitions."""

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)
        self.disk = self.context.params.disk

    def run(self):
        with (
            complete_step("Formatting file systems on disk"),
            contextlib.ExitStack() as stack,
        ):
            disk = pathlib.Path(self.context.params.disk)
            if disk.suffix == ".img" or disk.suffix == ".raw":
                self.disk = stack.enter_context(attach_image_loopback(self.disk))

            for index, part in enumerate(self.context.stage.filesystems, start=1):
                disk = self._get_partition_device(index, self.disk)
                if not os.path.exists(disk):
                    die(f"{disk} not found.")
                label = part.get("label", None)
                if label is None:
                    die("Partition label is not specified.")
                fs = part.get("fs", None)
                if fs is None:
                    die("Partition type is not specified.")

                self.make_filesystem(disk, part["name"], label, fs)

        show_disk(self.context.params.disk)

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

    def make_filesystem(self, disk, part, label, fs):
        """Format a file system onto disk slice."""
        match fs:
            case "vfat":
                command = ["mkfs.vfat", "-F", "32", "-n", label, disk]
            case "ext4" | "ext3":
                command = ["mkfs", "-F", "-t", fs, "-L", label, disk]
            case _:
                die(f"{fs} is not a supported type.")

        try:
            logging.debug(f"Formatting {disk}, name={part}, label={label}, fs={fs}.")
            subprocess.run(command, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            die(f"Failed to format {disk}: " + e.stderr.decode("utf-8").strip())
