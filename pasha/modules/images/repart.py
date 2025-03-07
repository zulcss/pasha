"""
Copyright (c) 2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import shutil
import subprocess
import sys

from pasha.context import Context
from pasha.log import complete_step, die
from pasha.modules.base import ModuleBase


class RepartImage(ModuleBase):
    """Create a disk image using repart."""

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        if not shutil.which("systemd-repart"):
            die(
                "systemd-repart binary is not installed",
                die="Install the package via 'apt-get install -y systemd",
            )

        self.context = Context(self.state, self.config, self.stage)

        # Loading parameters
        self.definitions = self.context.stage.get("definitions", None)
        self.esp = self.context.stage.get("esp", "512M")
        self.root = self.context.stage.get("root", "20G")

        if os.path.exists(self.context.params.disk):
            os.unlink(self.context.params.disk)

    def run(self):
        with complete_step(f"Creating {self.context.params.disk}"):
            if self.definitions is None:
                logging.info(
                    f"Using default disk configuration  "
                    f"(esp - {self.esp}, root - {self.root})"
                )
                self.create_default_partitions()
            self.create_disk()

    def create_default_partitions(self):
        """Create default partitions if repart definitions are not defined."""
        self.definitions = self.context.workspace.joinpath("repart-config")
        if self.definitions.exists():
            shutil.rmtree(self.definitions)
        self.definitions.mkdir(parents=True)

        with complete_step(f"Creating disk configurations in {self.definitions}"):
            logging.info("Creating esp definition")
            (self.definitions / "00-esp.conf").write_text(
                f"""\
                [Partition]
                Type=esp
                Format=vfat
                CopyFiles=/boot:/
                SizeMinBytes={self.esp}
                SizeMaxBytes={self.esp}
                """
            )

            logging.info("Creating root definitions")
            (self.definitions / "10-root.conf").write_text(
                f"""\
                [Partition]
                Type=root
                Format=ext4
                CopyFiles=/
                SizeMinBytes={self.root}
                """
            )

    def create_disk(self):
        """Create a disk using systemd-repart."""

        cmd = [
            "systemd-repart",
            "--empty=create",
            "--discard=no",
            "--size=auto",
            "--no-pager",
            "--dry-run=no",
            "--root",
            self.context.root,
            "--definitions",
            self.definitions,
        ]

        try:
            subprocess.run(cmd + [self.context.params.disk], check=True)
        except subprocess.CalledProcessError as error:
            die(f"Failed to run systemd-repart: {error}")
