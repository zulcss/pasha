"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging

from pasha import exceptions, utils

log = logging.getLogger(__name__)


def unpack(archive, rootfs):
    log.info(f"Unpacking {archive}.")
    ret, output = utils.run_command(
        ["tar", "-C", rootfs, "--exclude=./dev/*", "-zxf", archive, "--numeric-owner"]
    )
    if ret != 0:
        raise exceptions.CommandError(f"Failed to unpack {archive}: {output}")
