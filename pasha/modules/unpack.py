"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import shutil

from pasha import utils
from pasha.archive import unpack
from pasha.modules.base import ModuleBase
from pasha.mount import mount, umount


class Unpack(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")

        self.logging = logging.getLogger(__name__)

        # supported compression levels
        self.compression = {
            "tgz": "-zxf",
            "squashfs": "squashfs",
        }

    def run(self):
        mount_flag = self.stage.get("mount")
        compression = self.stage.get("compression")
        sources = self.stage.get("sources")
        if sources:
            if self.rootfs.exists():
                self.logging.info(f"Found older {self.rootfs} removing.")
                shutil.rmtree(self.rootfs)
            self.rootfs.mkdir(parents=True, exist_ok=True)

            if mount_flag:
                mount(self.config.params.disk, self.rootfs)

            for source in sources:
                if source.startswith("http") or source.startswith("https"):
                    source = utils.fetch(source)

                if os.path.exists(source):
                    self._unpack(source, self.rootfs, compression)
                else:
                    raise Exception(f"Could not find {source}.")

            if mount_flag:
                umount(self.rootfs)

        else:
            raise Exception("Unable to determine tarball sources.")

    def _unpack(self, source, rootfs, compression):
        if compression == "tgz":
            self.logging.info("Unpacking tarball.")
            unpack(source, self.rootfs)

        if compression == "squashfs":
            self.logging.info("Unpacking squashfs image.")
            utils.run_command(["unsquashfs", "-f", "-d", rootfs, source])
