"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import pathlib
import shutil
import subprocess

from rich.console import Console

from pasha import exceptions, utils
from pasha.context import Context
from pasha.log import complete_step, die
from pasha.modules.base import ModuleBase
from pasha.mount import mount_disk
from pasha.ostree import cli, ostree_ref

console = Console()


class OstreeBase(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.context = Context(self.state, self.config, self.stage)

        if not shutil.which("ostree"):
            die(
                "Unable to find 'ostree'",
                hint="As root run 'apt-get install -y ostree' to install ostree",
            )

        self.context = Context(self.state, self.config, self.stage)
        self.repo = pathlib.Path(self.context.params.repository)
        self.branch = self.context.params.branch

    def run(self):
        pass


class OstreeInit(OstreeBase):
    """Initialize an ostree Repository."""

    def run(self):
        self.mode = self.context.stage.get("mode", "bare")

        with complete_step("Initializing ostree repository"):
            self.repo.mkdir(parents=True, exist_ok=True)
            cli("init", repo=self.repo, mode=self.mode)


class OstreePullLocal(OstreeBase):
    """Pull ostree branch from local repository."""

    def run(self):
        with mount_disk(self.context, self.context.root):
            repo = self.context.root.joinpath("ostree/repo")
            if not repo.exists():
                die(f"{repo} does not exist.")
            try:
                subprocess.run(
                    ["ostree", "pull-local", "--repo", repo, self.repo, self.branch],
                    check=True,
                )
                subprocess.run(
                    f"ostree summary -u --repo={repo}", shell=True, check=True
                )
            except subprocess.CalledProcessError as e:
                die(f"Failed to pull: " + e.stderr.decode("utf-8").strip())


class OstreePullRemote(OstreeBase):
    """Pull ostree branch from remote repository."""

    def run(self):
        with mount_disk(sef.context, self.context.root):
            repo = self.context.root.joinpath("ostree/repo")
            if not repo.exists():
                die(f"{repo} does not exist.")
            with complete_step(f"Pulling from {self.repo}"):
                try:
                    subprocess.run(
                        [
                            "ostree",
                            "remote",
                            "--repo={0}".format(repo),
                            "add",
                            "--no-gpg-verify",
                            "elxr-edge",
                            self.repo,
                        ],
                        check=True,
                    )
                    subprocess.run(
                        [
                            "ostree",
                            "pull",
                            "--repo={0}".format(repo),
                            "elxr-edge",
                            self.branch,
                        ],
                        check=True,
                    )
                    subprocess.run(
                        f"ostree summary -u --repo={repo}", shell=True, check=True
                    )
                except subprocess.CalledProcessError as e:
                    die(f"Failed to pull: " + e.stderr.decode("utf-8").strip())


class OstreeDeploy(OstreeBase):
    """Deploy an ostree branch to a mounted disk."""

    def run(self):
        self.device = self.config.params.disk
        self.kernel_args = self.stage.kernel_args
        self.mode = self.context.stage.get("mode", "bare")

        with mount_disk(self.context.params.disk, self.context.root):
            # Initialize an empty repo
            repo = self.context.root.joinpath("ostree/repo")
            repo.mkdir(parents=True)
            cli("init", repo=repo, mode=self.mode)

            # Running init-fs
            with console.status(f"Pulling {self.branch} from {self.repo}."):
                cli("pull-local", self.repo, self.branch, repo=repo)
                cli("summary", "-u", repo=repo)
                cli(
                    "admin",
                    "init-fs",
                    "--modern",
                    self.context.root,
                    sysroot=self.context.root,
                )
                cli("admin", "stateroot-init", "elxr", sysroot=self.context.root)

            kargs = []
            for arg in self.kernel_args:
                kargs += [f"--karg-append={arg}"]

            cli(
                "admin",
                "deploy",
                self.branch,
                *kargs,
                sysroot=self.context.root,
                os="elxr",
            )

            with complete_step("Setting up home."):
                # create home directory manually as the ostree admin init-fs with modern
                # parameter did not create it.
                self.context.root.joinpath("home").mkdir(parents=True, exist_ok=True)


class OstreePrep(OstreeBase):
    """Create an ostree branch from a chroot."""

    def run(self):
        with complete_step(f"Converting {self.context.config.name} to ostree."):
            self.setup_boot()
            self.convert_to_ostree()

    def convert_to_ostree(self):
        """Convert Debian rootfs to ostree."""
        with complete_step("Moving /var/lib/dpkg to /usr/share/dpkg/database."):
            os.rename(
                self.context.root.joinpath("var/lib/dpkg"),
                self.context.root.joinpath("usr/share/dpkg/database"),
            )

        with complete_step("Moving /etc to /usr/etc."):
            shutil.move(
                self.context.root.joinpath("etc"), self.context.root.joinpath("usr")
            )

        with complete_step("Setting up /ostree and /sysroot."):
            self.context.root.joinpath("ostree").mkdir(parents=True, exist_ok=True)
            self.context.root.joinpath("sysroot").mkdir(parents=True, exist_ok=True)

        with complete_step("Setting up symlinks."):
            # do not create /opt -> /var/opt
            TOPLEVEL_LINKS = {
                "media": "run/media",
                "mnt": "var/mnt",
                "ostree": "sysroot/ostree",
                "root": "var/roothome",
                "srv": "var/srv",
                "usr/local": "../var/usrlocal",
                "home": "var/home",
            }
            fd = os.open(self.context.root, os.O_DIRECTORY)
            for l, t in TOPLEVEL_LINKS.items():
                shutil.rmtree(self.context.root.joinpath(l))
                os.symlink(t, l, dir_fd=fd)

    def setup_boot(self):
        """Setup up the ostree boot directory."""
        with complete_step(f"Preparing bootloader"):
            bootdir = self.context.root.joinpath("boot")
            targetdir = self.context.root.joinpath("usr/lib/modules")

            for item in os.listdir(bootdir):
                if item.startswith("vmlinuz"):
                    _, version = item.split("-", 1)

            for item in os.listdir(bootdir):
                if item.startswith("vmlinuz"):
                    vmlinuz = item
                    _, version = item.split("-", 1)
                elif item.startswith("initrd.img") or item.startswith("initramfs"):
                    initrd = item
                else:
                    # Move all other artifacts as is
                    shutil.move(
                        os.path.join(bootdir, item), targetdir.joinpath(version)
                    )

            kernel = bootdir.joinpath(vmlinuz)
            logging.info(f"Found {kernel}")
            os.rename(kernel, targetdir.joinpath(f"{version}/vmlinuz"))

            initrd = bootdir.joinpath(initrd)
            logging.info(f"Found {initrd}")
            os.rename(initrd, targetdir.joinpath(f"{version}/initramfs.img"))


class OstreeConfig(OstreeBase):
    """Set ostree configuration parameters."""

    def run(self):
        disk = self.context.params.disk
        if not os.path.exists(disk):
            die(f"Unable to find {disk}.")
        with mount_disk(disk, self.context.rootfs):
            self.ostree_config = self.context.stage.config
            repo = self.context.rootfs.joinpath("ostree/repo")
            if not os.path.exists(repo):
                die(f"{repo} does not exist.")

            for key, val in self.ostree_config.items():
                try:
                    subprocess.run(
                        ["ostree", "config", "set", "--repo", repo, key, str(val)],
                        check=True,
                    )
                except subprocess.CalledProcessError as e:
                    die(f"Failed to set ostree config parameter: {e}")


class OstreeCommit(OstreeBase):
    def run(self):
        with console.status(f"Committing {self.context.params.branch} to {self.repo}."):
            cli(
                "commit",
                str(self.context.root),
                repo=self.repo,
                branch=self.branch,
                subject="Initial commit",
            )

        logging.info("Updating summary of ostree repository.")
        subprocess.run(["ostree", "summary", "-u", f"--repo={self.repo}"], check=True)
