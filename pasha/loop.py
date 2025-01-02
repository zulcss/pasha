"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import contextlib
import logging
import subprocess

from pasha.log import complete_step


@contextlib.contextmanager
def attach_image_loopback(disk):
    """Scan, attach, and detach a loop device for an image.

    :param disk: Disk setup loop device/detach to.
    """
    if disk is None:
        yield None
        return

    with complete_step(f"Attaching image file {disk}"):
        c = subprocess.run(
            ["losetup", "--find", "--show", "--partscan", disk],
            stdout=subprocess.PIPE,
            check=True,
        )
        loopdev = c.stdout.decode("utf-8").strip()
    try:
        yield loopdev
    finally:
        with complete_step(f"Detaching image file {disk}"):
            subprocess.run(["losetup", "--detach", loopdev], check=True)
