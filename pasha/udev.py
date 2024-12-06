"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import subprocess
import sys

LOG = logging.getLogger(__name__)


def settle():
    try:
        LOG.debug("Running udevadm settle")
        subprocess.run(["udevadm", "settle"], check=True)
    except subprocess.SubprocessError as error:
        LOG.error(f"Failed to run 'udevadm settle': {error}")
        sys.exit(1)
