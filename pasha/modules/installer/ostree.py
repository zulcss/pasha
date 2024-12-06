"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import pathlib
import shutil

from pasha import exceptions, utils
from pasha.modules.base import ModuleBase


def ostree(*args, **kwargs):
    args = list(args) + [f"--{k}={v}" for k, v in kwargs.items()]
    utils.run_command(["ostree"] + args)


class OstreeInit(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)
        self.repo = pathlib.Path(self.config.params.repository)
        self.branch = self.config.params.branch
        self.mode = self.stage.get("mode", "bare")
        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")

    def run(self):
        self.logging.info("Unpacking source.")

        if os.path.ismount(self.rootfs):
            self.repo = self.rootfs.joinpath("ostree/repo")

        self.logging.info(f"Creating {self.repo}")
        if not self.repo.exists():
            self.repo.mkdir(parents=True, exist_ok=True)
        utils.run_command(
            ["ostree", "init", "--repo", self.repo, "--mode", f"{self.mode}"]
        )


class OstreePullLocal(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)
        self.device = self.config.params.disk
        self.repo = self.config.params.repository
        self.branch = self.config.params.branch
        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")

    def run(self):
        repo = self.rootfs.joinpath("ostree/repo")
        self.logging.info(f"Pulling {self.branch} from {self.repo}")
        if not repo.exists():
            raise exeptions.ConfigError(f"{repo} does not exist.")

        utils.run_command(
            ["ostree", "pull-local", "--repo", repo, self.repo, self.branch]
        )

        self.logging.info("Updating summary of ostree repository")
        utils.run_command(f"ostree summary -u --repo={repo}", shell=True)


class OstreePullRemote(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)
        self.device = self.config.params.disk
        self.repo = self.config.params.repository
        self.branch = self.config.params.branch
        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")

    def run(self):
        repo = self.rootfs.joinpath("ostree/repo")
        if not repo.exists():
            raise exceptions.ConfigError(f"{repo} does not exist.")

        if self.repo.startswith("http"):
            self.logging.info(f"Pulling from {self.repo}")
            utils.run_command(
                [
                    "ostree",
                    "remote",
                    "--repo={0}".format(repo),
                    "add",
                    "--no-gpg-verify",
                    "elxr-edge",
                    self.repo,
                ]
            )
            utils.run_command(
                ["ostree", "pull", "--repo={0}".format(repo), "elxr-edge", self.branch]
            )

            self.logging.info("Updating summary of ostree repository")
            utils.run_command(f"ostree summary -u --repo={repo}", shell=True)


class OstreeDeploy(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)
        self.device = self.config.params.disk
        self.repo = self.config.params.repository
        self.branch = self.config.params.branch
        self.kernel_args = self.stage.kernel_args
        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")

    def run(self):
        self.logging.info(f"Configuring {self.device} for ostree.")
        utils.run_command(["ostree", "admin", "init-fs", self.rootfs])
        utils.run_command(
            ["ostree", "admin", "os-init", "--sysroot", self.rootfs, "elxr"]
        )

        self.logging.info(f"Deploying {self.branch}")
        ostree_deploy = [
            "ostree",
            "admin",
            "deploy",
            "--sysroot",
            self.rootfs,
            "--os",
            "elxr",
            self.branch,
        ]
        for arg in self.kernel_args:
            ostree_deploy.append(f"--karg={arg}")
        utils.run_command(ostree_deploy)

        self.logging.info("Restoring /var")
        for d in self.rootfs.glob("ostree/deploy/elxr/deploy/*.0"):
            repo_root = d
        var_to = self.rootfs.joinpath("ostree/deploy/elxr")
        var_from = os.path.join(repo_root, "usr/rootdirs/var")
        self.logging.debug(f"Copying {var_from} -> {var_to}")
        cmd = f"cp -af {var_from} {var_to}"
        utils.run_command(cmd, shell=True)


class OstreePrep(ModuleBase):
    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        self.logging = logging.getLogger(__name__)
        self.repo = self.config.params.repository
        self.branch = self.config.params.branch
        self.target = self.config.params.source
        self.rootfs = self.state.workspace.joinpath(f"{self.config.name}/rootfs")

    def run(self):
        self._setup_boot(
            self.rootfs.joinpath("boot"), self.rootfs.joinpath("usr/lib/modules")
        )
        self._convert_to_ostree()
        self.logging.info("Committing to ostree")
        ostree(
            "commit",
            str(self.rootfs),
            repo=self.repo,
            branch=self.branch,
            subject="Initial commit",
        )

        self.logging.info("Updating summary of ostree repository")
        utils.run_command(f"ostree summary -u --repo={self.repo}", shell=True)

    def _convert_to_ostree(self):
        """Convert Debian rootfs to ostree."""
        CRUFT = [
            "boot/initrd.img",
            "boot/vmlinuz",
            "initrd.img",
            "initrd.img.old",
            "vmlinuz",
            "vmlinuz.old",
        ]

        # Remove unnecessary files
        self.logging.info("Removing unnecessary files.")
        for c in CRUFT:
            try:
                os.remove(self.rootfs.joinpath(c))
            except OSError:
                pass

        # Copying /var
        self.logging.info("Moving /var/lib/dpkg to /usr/share/dpkg/database.")
        os.rename(
            self.rootfs.joinpath("var/lib/dpkg"),
            self.rootfs.joinpath("usr/share/dpkg/database"),
        )
        self.logging.info("Backup /var.")
        dir_perm = 0o755
        os.mkdir(self.rootfs.joinpath("usr/rootdirs"), dir_perm)
        self.logging.debug("Moving /var to /usr/rootdirs.")
        os.rename(
            self.rootfs.joinpath("var"),
            self.rootfs.joinpath("usr/rootdirs/var"),
        )
        os.mkdir(self.rootfs.joinpath("var"), dir_perm)

        # Setup and split out etc
        self.logging.info("Moving /etc to /usr/etc.")
        shutil.move(self.rootfs.joinpath("etc"), self.rootfs.joinpath("usr"))

        self.logging.info("Setting up /ostree and /sysroot.")
        try:
            self.rootfs.joinpath("ostree").mkdir(parents=True, exist_ok=True)
            self.rootfs.joinpath("sysroot").mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

        self.logging.info("Setting up symlinks.")
        TOPLEVEL_LINKS = {
            "media": "run/media",
            "mnt": "var/mnt",
            "opt": "var/opt",
            "ostree": "sysroot/ostree",
            "root": "var/roothome",
            "srv": "var/srv",
            "usr/local": "../var/usrlocal",
            "home": "var/home",
        }
        fd = os.open(self.rootfs, os.O_DIRECTORY)
        for l, t in TOPLEVEL_LINKS.items():
            shutil.rmtree(self.rootfs.joinpath(l))
            os.symlink(t, l, dir_fd=fd)

    def _setup_boot(self, bootdir, targetdir):
        """Setup up the ostree bootdir"""
        vmlinuz = None
        initrd = None
        dtbs = None
        version = None

        for item in os.listdir(bootdir):
            if item.startswith("vmlinuz"):
                _, version = item.split("-", 1)

        targetdir = os.path.join(targetdir, version)
        try:
            os.mkdir(targetdir)
        except OSError:
            pass

        for item in os.listdir(bootdir):
            if item.startswith("vmlinuz"):
                assert vmlinuz is None
                vmlinuz = item
                _, version = item.split("-", 1)
            elif item.startswith("initrd.img") or item.startswith("initramfs"):
                assert initrd is None
                initrd = item
            elif item.startswith("dtbs"):
                assert dtbs is None
                dtbs = os.path.join(bootdir, item)
            else:
                # Move all other artifacts as is
                shutil.move(os.path.join(bootdir, item), targetdir)
        assert vmlinuz is not None

        os.rename(
            os.path.join(bootdir, vmlinuz),
            os.path.join(targetdir, "vmlinuz"),
        )

        if initrd is not None:
            os.rename(
                os.path.join(bootdir, initrd),
                os.path.join(targetdir, "initramfs.img"),
            )
