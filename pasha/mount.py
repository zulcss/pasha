"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import contextlib
import logging
import subprocess

from pasha.log import complete_step, die


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

    logging.debug("Mounting image...")
    subprocess.run(
        ["systemd-dissect", "--mount", "--mkdir", disk, rootfs],
        capture_output=True, check=True)

    try:
        yield
    finally:
        logging.debug("Umounting image...")
        subprocess.run(
            ["systemd-dissect", "--umount", rootfs],
            capture_output=True, check=True)
