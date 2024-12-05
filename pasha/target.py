"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import subprocess
import sys
import time

from pasha import block, udev

LOG = logging.getLogger(__name__)


class RunInTarget(object):
    """Run a command in a chroottable target."""

    def __init__(self, image, rootfs, mounts):
        self.image = image
        self.rootfs = rootfs
        self.mounts = mounts
        self.device = None
        # File systems to mount from the host.
        self.fs = ["dev", "proc", "sys"]

    def __enter__(self):
        """Create loopback device and mount it."""
        self.device = block.create_loopback(self.image)
        udev.settle()
        try:
            self.mount()
        except RuntimeError as e:
            LOG.error(f"{e} Cleaning up and Exiting!!")
            try:
                self.umount()
            except RuntimeError:
                pass  # Ignore unmount issues, their expected
            block.remove_loopback(self.device)
            sys.exit(1)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Umount and remove loopback device."""
        try:
            self.umount()
        except RuntimeError as e:
            LOG.error(f"{e} Cleaning up and Exiting!!")
            block.remove_loopback(self.device)
            sys.exit(1)
        block.remove_loopback(self.device)
        udev.settle()

    def mount(self):
        """Setup mount points from the image so that the command in a
        chroot environment can be executed.
        """
        for m in self.mounts:
            disk = f"/dev/disk/by-partlabel/{m.label}"
            LOG.info(f"Finding {disk}.")
            for retry in range(0, 5):
                if os.path.exists(disk):
                    break
                time.sleep(0.25)
            if not os.path.exists(disk):
                LOG.error(f"ERROR. {disk} not found.")
                raise RuntimeError("Unable to mount all required mounts.")

            target = m.target
            if target == "/":
                LOG.info(f"Found {m.target} mounting on {self.rootfs}.")
                self.rootfs.mkdir(parents=True, exist_ok=True)
                target = self.rootfs
            else:
                target = self.rootfs.joinpath(m.target)
                LOG.info(f"Found {m.target} mounting on {target}.")
                if not target.exists():
                    LOG.info(f"Creating {target}")
                    target.mkdir(parents=True, exist_ok=True)

            try:
                LOG.debug(f"Mounting {disk} on {target}.")
                subprocess.run(["mount", "-t", m.fs, disk, target], check=True)
            except subprocess.CalledProcessError as error:
                LOG.error(f"Failed to mount {target}: {error}")
                raise RuntimeError("Unable to mount all required mounts.")

        for f in self.fs:
            bind = self.rootfs.joinpath(f)
            LOG.debug(f"Bind mounting {bind}.")
            try:
                subprocess.run(["mount", "-o", "bind", f"/{f}", bind], check=True)
            except subprocess.CalledProcessError as error:
                LOG.error(f"Failed to bind {bind}: {error}")
                raise RuntimeError("Unable to mount all required mounts.")

    def umount(self):
        """Umount the previously mounted target image."""
        try:
            LOG.debug(f"Umounting {self.rootfs}.")
            subprocess.run(["umount", "-l", self.rootfs], check=True)
        except subprocess.CalledProcessError as error:
            LOG.error(f"Failed to umount {self.rootfs}: {error}")
            raise RuntimeError("Unable to unmount all mounts.")

    def run(self, args):
        """Run a command in a previously mounted environment."""
        try:
            LOG.debug(f"Running {args}.")
            subprocess.run(["chroot", self.rootfs] + args, check=True)
        except subprocess.CalledProcessError as error:
            errmsg = f"Failed to run command: {error}"
            LOG.error(errmsg)
            raise RuntimeError(errmsg)
