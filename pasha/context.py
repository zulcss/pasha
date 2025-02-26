"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import os
import pathlib


class Context:
    """State related properties."""

    def __init__(self, state, config, stage):
        # Parameters passed by rucksack CLI.
        self.state = state

        # Manifest configuration passed by rucksack.
        self.config = config

        # Manifest configuration needed by the pasha module.
        self.stage = stage

        # Global parameters passed by the manifest configuration
        # (can be empty).
        self.params = config.get("params", {})

        # Path to the rucksack workspace directory.
        self.workspace = state.workspace.joinpath(config.name)

        # Path to the unpacked rootfs or image mount point.
        self.rootfs = self.workspace.joinpath("rootfs")

        # Create the workspace directory.
        self.workspace.mkdir(parents=True, exist_ok=True)

    @property
    def root(self):
        """Path to the unpacked rootfs or image mount point."""
        return self.rootfs

    @property
    def workdir(self):
        """Path to workspace."""
        return self.workspace

    @property
    def staging(self):
        """Current directory path, used for storing logfiles."""
        return pathlib.Path(os.getcwd()).resolve()
