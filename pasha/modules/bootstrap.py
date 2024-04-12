"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import shutil

from pasha import exceptions, utils
from pasha.modules.base import ModuleBase


class Bootstrap(ModuleBase):

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)
        self.rootfs = self.state.workspace.joinpath("rootfs")

    def run(self):
        self.logging.debug("in bootstrap")

        self.mmdebstrap = shutil.which("mmdebstrap")
        if not self.mmdebstrap:
            raise Exception("mmdebstrap is not found.")

        target = self.stage.get("target")
        if target is None:
            raise exceptions.ConfigError("target is not specified.")

        suite = self.stage.get("suite")
        if suite is None:
            raise exceptions.ConfigErrror("suite is not found.")
            if suite not in ["bookworm", "trixie", "testing", "sid"]:
                raise exceptions.ConfigError(f"{suite} is not a supported  suite.")

        self.logging.info("Running mmdebstrap.")

        cmd = [self.mmdebstrap, "--architecture", self.config.architecture, "--verbose"]

        # Extend mmdebstrap configuration options, see manpage for details.
        packages = self.stage.get("packages")
        if packages:
            cmd.extend([f"--include={', '.join(packages)}"])
        repo = self.stage.get("repo")
        if repo:
            if not os.path.isfile(repo) and not os.path.exists():
                raise exceptions.ConfigError("Repo configuration is not a file")
            repo = self.workspace.joinpath(repo)
        customize_hooks = self.stage.get("customize_hooks")
        if customize_hooks:
            cmd.extend([f"--customize-hook={hook}" for hook in customize_hooks])
        components = self.stage.get("components")
        if components:
            cmd.extend([f"--components={','.join(components)}"])
        variant = self.stage.get("variant")
        if variant:
            cmd.extend([f"--variant={variant}"])
        hooks = self.stage.get("hooks")
        if hooks:
            cmd.extend([f"--hook-directory={hook}" for hook in hooks])
        setup_hooks = self.stage.get("setup_hooks")
        if setup_hooks:
            cmd.extend([f"--setup-hook={hook}" for hook in setup_hooks])
        extract_hooks = self.stage.get("extract_hooks")
        if extract_hooks:
            cmd.extend([f"--extract-hook={hook}" for hook in extract_hooks])
        essential_hooks = self.stage.get("options.essential_hooks")
        if essential_hooks:
            cmd.extend([f"--essential-hook={hook}" for hook in essential_hooks])
        apt_hooks = self.stage.get("apt_hooks")
        if apt_hooks:
            cmd.extend([f"--aptopt={hook}" for hook in apt_hooks])
        mode = self.stage.get("mode")
        if mode:
            cmd.extend([f"--mode={mode}"])
        keyring = self.stage.get("keyring")
        if keyring:
            cmd.extend([f"--keyring={hook}" for hook in keyring])
        dpkg_opts = self.stage.get("dpkgopt")
        if dpkg_opts:
            cmd.extend([f"--dpkgopts='{hook}'" for hook in dpkg_opts])
        format = self.stage.get("format")
        if format:
            cmd.extend([f"--format={format}"])

        cmd.extend([suite, target])
        if repo is not None:
            # include our mirror from the manifest.
            cmd.extend([repo])
        utils.run_command(cmd)

    def validate(self):
        pass
