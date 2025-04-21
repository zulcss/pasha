"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import contextlib
import json
import logging
import os
import subprocess
import time

from pasha.log import complete_step, die


def _get_partitions(blkdev):
    """Returns a list of partition device node paths for a block device.

    :param blkdev: path to the block device file/node
    """

    # Does not work with BSD partition table.
    c = subprocess.run(
        ["sfdisk", "-J", blkdev],
        stdout=subprocess.PIPE,
        check=True,
    )

    # Parse the output from "sfdisk" command to find the list of partitions.
    parsed = json.loads(c.stdout)

    return [entry["node"] for entry in parsed["partitiontable"]["partitions"]]


def _wait_for_file(path, timeout_sec=60):
    """Blocks until the file at given path exsits.

    :param path: The path to the file we wait for.
    """

    t_start_wait = time.time()

    while True:
        if os.path.lexists(path):
            return
        if time.time() - t_start_wait > timeout_sec:
            die(f"Timeout waiting for the existence of {path}")
        time.sleep(0.5)


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
        # Wait for all partitions to become available.
        part_lst = _get_partitions(loopdev)
        logging.debug(f"Waiting for {len(part_lst)} partitions on {loopdev}")
        for part in part_lst:
            logging.debug(f"attach_image_loopback(): Waiting for {part}")
            _wait_for_file(part)

        # All partitions associated with the loopback device are available.
        yield loopdev
    finally:
        with complete_step(f"Detaching image file {disk}"):
            subprocess.run(["losetup", "--detach", loopdev], check=True)
