"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import shutil
import subprocess

from pasha import exceptions
from pasha.context import Context
from pasha.log import complete_step, die
from pasha.modules.base import ModuleBase


class Bootstrap(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        if not shutil.which("mmdebstrap"):
            die(
                "Could not find mmdebstrap binary.",
                hint=("Install mmdebstrap by running 'apt-get install -y mmdebstrap'."),
            )

        self.context = Context(self.state, self.config, self.stage)
        self.target = self.context.stage.get("target", None)
        if self.target is None:
            raise exceptions.ConfigError("target is not specified.")
        self.suite = self.context.stage.get("suite", None)
        if self.suite is None:
            raise exceptions.ConfigError("suite is not found.")

    def run(self):
        """Bootstrap Debian based system."""
        with complete_step(f"Bootstrapping {self.context.config.name}"):
            logfile = self.context.staging.joinpath("mmdebstrap.log")
            cmd = [
                "mmdebstrap",
                f"--architecture={self.context.stage.architecture}",
            ]
            if self.context.state.debug:
                cmd.extend(["--verbose"])

            """
            Extend mmdebstrap configuration options, see man page for details.
            """
            packages = self.context.stage.get("packages")
            if packages:
                """Install additional packages into the chroot."""
                logging.debug("Adding additional packages.")
                for sub_packages in packages:
                    logging.info(f"Additional packages to be installed: {sub_packages}")
                    for package in sub_packages.split():
                        cmd.extend([f"--include={package}"])

            repo = None
            mirrors = self.context.stage.get("mirrors")
            if mirrors:
                """Bootstrap with additional mirrors."""
                logging.debug("Adding additional mirrors.")
                repo = self.context.staging.joinpath("mirror.list")
                if repo.exists():
                    os.unlink(repo)
                with open(repo, "w") as f:
                    for mirror in mirrors:
                        f.write(f"{mirror}\n")
                    if mirror.startswith("deb "):
                        src_mirror = "# deb-src " + mirror.removeprefix("deb ")
                        f.write(f"{src_mirror}\n")

            customize_hooks = self.context.stage.get("customize_hooks")
            if customize_hooks:
                """Execute commands after the chroot is setup and all packages
                get installed.
                """
                logging.debug("Adding custom hooks.")
                cmd.extend([f"--customize-hook={hook}" for hook in customize_hooks])

            components = self.context.stage.get("components")
            if components:
                """List of components like main, contrib, non-free, etc."""
                logging.debug("Adding additional components.")
                cmd.extend([f"--components={','.join(components)}"])

            variant = self.context.stage.get("variant")
            if variant:
                """Choose which package set to install."""
                logging.debug("Adding variant.")
                cmd.extend([f"--variant={variant}"])

            hooks = self.context.stage.get("hooks")
            if hooks:
                """Execute scripts in directory."""
                logging.debug("Adding hooks.")
                cmd.extend([f"--hook-directory={hook}" for hook in hooks])

            setup_hooks = self.context.stage.get("setup_hooks")
            if setup_hooks:
                """Execute arbitrary command right after initial setup."""
                logging.debug("Adding setup hooks.")
                cmd.extend([f"--setup-hook={hook}" for hook in setup_hooks])

            extract_hooks = self.context.stage.get("extract_hooks")
            if extract_hooks:
                """Execute arbitrary commands after the essential packages
                have been extracted.
                """
                logging.debug("Adding extract hooks.")
                cmd.extend([f"--extract-hook={hook}" for hook in extract_hooks])

            essential_hooks = self.context.stage.get("options.essential_hooks")
            if essential_hooks:
                """Execute arbitrary commands after the essential packages
                have been installed.
                """
                logging.debug("Adding essential hooks.")
                cmd.extend([f"--essential-hook={hook}" for hook in essential_hooks])

            apt_hooks = self.context.stage.get("apt_hooks")
            if apt_hooks:
                """Pass options to apt, which will be permanently add to the
                chroot.
                """
                logging.debug("Adding apt hooks.")
                cmd.extend([f"--aptopt={hook}" for hook in apt_hooks])

            mode = self.context.stage.get("mode")
            if mode:
                """Choose how to perform the chroot operation."""
                logging.debug("Adding mode.")
                cmd.extend([f"--mode={mode}"])

            keyring = self.context.stage.get("keyring")
            if keyring:
                """Change the default keyring to be used by apt during the
                initial setup.
                """
                logging.debug("Adding additional keyring.")
                cmd.extend([f"--keyring={hook}" for hook in keyring])

            dpkg_opts = self.context.stage.get("dpkgopt")
            if dpkg_opts:
                """Pass arbitrary options to dpkg."""
                logging.debug("Adding additional dpkg options.")
                cmd.extend([f"--dpkgopt={hook}" for hook in dpkg_opts])

            format = self.context.stage.get("format")
            if format:
                """Choose the output format."""
                logging.debug("Adding format.")
                cmd.extend([f"--format={format}"])

            cache_proxy = getattr(self.state, "cache_proxy", None)
            if cache_proxy:
                """Configure cache proxy for package caching."""
                logging.debug("Adding cache proxy.")
                cmd.extend([f'--aptopt=Acquire::http::Proxy "{cache_proxy}"'])

            cmd.extend([self.context.stage.suite, self.context.stage.target])
            if repo:
                cmd.extend([repo])

            logging.info(f"Creating Debian system for {self.context.config.name}.")
            try:
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
                with open(logfile, "w") as log_file:
                    for line in proc.stdout:
                        if self.context.state.debug:
                            logging.info(line.strip())
                        log_file.write(line)
                proc.wait()
                if proc.returncode != 0:
                    logging.info(
                        f"mmdebstrap failed with return code - {proc.returncode}"
                    )
                    die(
                        f"Failed to run mmdebstrap.",
                        hint=(f"Please see {logfile}."),
                    )
            except Exception as e:
                die(
                    f"Failed to run mmdebstrap.",
                    hint=(f"Please see {logfile}."),
                )
