"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import shutil

<<<<<<< HEAD
from omegaconf import OmegaConf

from pasha import exceptions
from pasha.archive import unpack
from pasha.mount import mount
from pasha.mount import umount
from pasha.modules.base import ModuleBase
=======
from pasha.archive import unpack
from pasha.modules.base import ModuleBase
from pasha.mount import mount
from pasha.mount import umount
>>>>>>> 9ac3dfe (add modules)
from pasha import utils


class Unpack(ModuleBase):

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage
        self.rootfs = self.state.workspace.joinpath(
<<<<<<< HEAD
                f"{self.config.name}/rootfs")
=======
            f"{self.config.name}/rootfs")
>>>>>>> 9ac3dfe (add modules)

        self.logging = logging.getLogger(__name__)

        # supported compression tevels
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
                    raise Exception(f"Couldnt find {source}.")

            if mount_flag:
<<<<<<< HEAD
               umount(self.rootfs)
=======
                umount(self.rootfs)
>>>>>>> 9ac3dfe (add modules)

        else:
            raise Exception("Unable to determine tarball sources.")

<<<<<<< HEAD
=======
    def validate(self):
        pass

>>>>>>> 9ac3dfe (add modules)
    def _unpack(self, source, rootfs, compression):
        if compression == "tgz":
            self.logging.info("Unpackging tarball.")
            unpack(source, self.rootfs)

        if compression == "squashfs":
            self.logging.info("Unpacking squashfs image.")
            utils.run_command(
                ["unsquashfs", "-f", "-d", rootfs, source])
<<<<<<< HEAD

=======
>>>>>>> 9ac3dfe (add modules)
