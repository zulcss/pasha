"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import shutil
import subprocess

from pasha import utils
from pasha.context import Context
from pasha.log import complete_step, die
from pasha.modules.base import ModuleBase


class BootOrder(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)

        if not shutil.which("efibootmgr"):
            die(f"efibootmgr is not installed.")

    def run(self):
        with complete_step("Running efibootmgr."):
            device = self.context.config.params.disk
            name = self.context.config.name
            output = subprocess.run(
                ["efibootmgr"], encoding="utf-8", capture_output=True, shell=True
            ).stdout
            for line in output.split("\n"):
                if not line.startswith("Boot") or "*" not in line:
                    continue
                # Boot0001* UEFI QEMU DVD-ROM QM00003 -> 0001* UEFI QEMU DVD-ROM QM00003
                line = line.removeprefix("Boot")
                # 0001* UEFI QEMU DVD-ROM QM00003 -> 0001
                oldbootnum = line.split("*")[0]
                # 0001* UEFI QEMU DVD-ROM QM00003 -> UEFI QEMU DVD-ROM QM00003
                oldbootname = line.split("*")[1]
                oldbootname = oldbootname.strip()
                # Remove existing old boot entry
                if oldbootname == name:
                    cmd = f"efibootmgr -b {oldbootnum} -B >/dev/null 2>&1"
                    subprocess.run(cmd, shell=True)

        # Add new boot entry to the top
        cmd = rf'efibootmgr -c -w -L "{name}" -d "{device}" -l "\EFI\BOOT\bootx64.efi"'
        subprocess.run(cmd, shell=True)
