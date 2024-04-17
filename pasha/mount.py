"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

from pasha import exceptions, utils


def mount(image, rootfs):
    """Mount an image via systemd-dissect."""
    (
        ret,
        output,
    ) = utils.run_command(["systemd-dissect", "-m", image, rootfs])
    if ret != 0:
        exceptions.CommandError(f"Failed to mount {image} on {rootfs}: {output}")
    return ret


def umount(rootfs):
    """Umount an image via systemd-dissect."""
    ret, output = utils.run_command(["systemd-dissect", "-u", rootfs])
    if ret != 0:
        exceptions.CommandError(f"Failed to umount {rootfs}: {output}")
    return ret
