"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import contextlib
import logging
import subprocess
import sys

LOG = logging.getLogger(__name__)


def is_block(device):
    """Check to see if device is a block device or not."""
    try:
        if stat.S_ISBLK(os.stat(device).st_mode):
            return True
        return False
    except Exception:
        raise Exception(f"{device} not found.")
    return False


def create_loopback(image):
    """Create a loopback deivce."""
    LOG.debug("Looking for free loopback device.")

    try:
        cp = subprocess.run(
            ["losetup", "--find", "--show", "--partscan", image],
            stdout=subprocess.PIPE,
            encoding="utf-8",
            check=True,
        )
        loopdev = cp.stdout.rstrip()
        LOG.debug(f"Found {loopdev}.")
        return loopdev
    except subprocess.CalledProcessError as error:
        LOG.error(f"Failed to find loopback device: {error}")
        sys.exit(1)


def remove_loopback(device):
    """Remove loopback device."""
    try:
        LOG.info(f"Removing {device}.")
        subprocess.run(["losetup", "-d", device], check=True)
    except subprocess.CalledProcessError as error:
        LOG.error(f"Failed to delete {image}: {error}")
        sys.exit(1)


@contextlib.contextmanager
def image(image):
    """Scan, attach, and detach a loopback device for a particular image."""
    LOG.debug("Looking for free loopback device.")
    loopdev = create_loopback(image)
    try:
        yield loopdev
    finally:
        remove_loopback(loopdev)
