"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import contextlib
import logging
import subprocess

from pasha.log import complete_step, die
from pasha.utils import systemd_version


@contextlib.contextmanager
def mount_disk(disk, rootfs):
    """Mount and unmount a disk.

    :params disk: string, block device to mount.
    :params rootfs; string, path to mount the block
                    device.
    """
    if disk is None:
        yield None
        return

    env = {}
    version = systemd_version()
    if version >= 261:
        logging.info("Newer systemd detected, applying work around.")
        env.update({"SYSTEMD_DISSECT_FSTYPE_XBOOTLDR": "ext4"})

    logging.debug("Mounting image...")
    subprocess.run(
        ["systemd-dissect", "--mount", "--mkdir", disk, rootfs],
        capture_output=True,
        check=True,
        env=env,
    )

    try:
        yield
    finally:
        logging.debug("Unmounting image...")
        subprocess.run(
            ["systemd-dissect", "--umount", rootfs], capture_output=True, check=True
        )


@contextlib.contextmanager
def mount_partition(disk, fs, target):
    with complete_step(f"Mounting {disk} on {target}."):
        subprocess.run(["mount", "-t", fs, disk, target])
        try:
            yield
        finally:
            logging.debug(f"Unmounting {target}.")
            subprocess.run(["umount", target], check=False)


@contextlib.contextmanager
def bind_mounts(sources, dest_root):
    for src in sources:
        dst = dest_root.joinpath(src)
        logging.debug(f"Mounting /{src} on {dst}.")
        subprocess.run(["mount", "-o", "bind", f"/{src}", str(dst)], check=True)
    try:
        yield
    finally:
        for src in reversed(sources):
            dst = dest_root.joinpath(src)
            logging.debug(f"Unmounting {dst}.")
            subprocess.run(["umount", dst], check=False)
