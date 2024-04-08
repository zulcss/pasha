"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""
import os
import stat


def is_block(device):
    """Check to see if device is a block device or not."""
    try:
        return stat.S_ISBLK(os.stat(device).st_mode)
    except OSError:
        if not os.path.exists(device):
            raise Exception(f"{device} not found.")
    return False
