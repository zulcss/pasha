"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import pathlib
import shutil
import subprocess

from pasha.archive import unpack
from pasha.context import Context
from pasha.log import complete_step
from pasha.modules.base import ModuleBase


class ContainerBase(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)
        self.source = self.context.config.params.source
        self.image = self.context.stage.image

        if not shutil.which("umoci"):
            raise Exception("umoci is not installed.")

    def run(self):
        pass


class ContainerCreate(ContainerBase):
    def run(self):
        (layer, tag) = self.image.split(":")

        with complete_step("Creating image layer"):
            if os.path.exists(layer):
                shutil.rmtree(layer)

            subprocess.run(["umoci", "init", "--layout", layer])
        with complete_step(f"Creating {self.image}"):
            subprocess.run(["umoci", "new", "--image", self.image])

        with complete_step(f"Unpacking {self.image} via umoci"):
            self.bundle_dir = self.context.workspace.joinpath(f"{layer}-unpacked")
            if os.path.exists(self.bundle_dir):
                shutil.rmtree(self.bundle_dir)

            subprocess.run(["umoci", "unpack", "--image", self.image, self.bundle_dir])
            with complete_step("Removing old rootfs"):
                rootfs = self.bundle_dir.joinpath("rootfs")
                if rootfs.exists():
                    shutil.rmtree(rootfs)

                rootfs.mkdir(parents=True, exist_ok=True)
                unpack(self.source, rootfs)

            with complete_step("Repacking OCI container image via umoci"):
                subprocess.run(
                    ["umoci", "repack", "--image", self.image, self.bundle_dir]
                )
