"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import os
import sys

from pasha import exceptions, utils

log = logging.getLogger(__name__)


def unpack(archive, rootfs):
    log.info(f"Unpacking {archive}.")
    ret, output = utils.run_command(
        ["tar", "-C", rootfs, "--exclude=./dev/*", "-zxf", archive, "--numeric-owner"]
    )
    if ret != 0:
        raise exceptions.CommandError(f"Failed to unpack {archive}: {output}")


def compress(archive, compressor="xz"):
    log.info(f"Compress {archive}.")

    if not os.path.exists(archive):
        log.error(f"{archive} not found")
        sys.exit(1)

    ncpu = os.cpu_count()
    if compressor == "xz":
        cmd = f"xz -9 -T{ncpu} -f --keep {archive}"
    elif compressor == "gzip":
        cmd = f"gzip -1 --keep -f {archive}"
    else:
        log.error(f"{compressor} not supported")
        sys.exit(1)

    return utils.run_command(cmd, shell=True)
