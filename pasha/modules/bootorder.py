"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging

from pasha import utils
from pasha.modules.base import ModuleBase


class BootOrder(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)

    def run(self):
        self.logging.info("Running efibootmgr.")
        device = self.config.params.disk
        name = self.config.name
        cmd = "efibootmgr"
        _, output = utils.run_command(cmd, shell=True)
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
                utils.run_command(cmd, shell=True)

        # Add new boot entry to the top
        cmd = rf'efibootmgr -c -w -L "{name}" -d "{device}" -l "\EFI\BOOT\bootx64.efi"'
        utils.run_command(cmd, shell=True)
