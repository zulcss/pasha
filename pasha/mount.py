"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

from pasha import utils


def mount(image, rootfs):
    utils.run_command(
        ["systemd-dissect", "-m", image, rootfs])


def umount(rootfs):
    utils.run_command(
        ["systemd-dissect", "-u", rootfs])
