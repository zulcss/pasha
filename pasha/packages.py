"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import os

from pasha import utils
from pasha.log import complete_step, die


def apt_update(context, env=None):
    """Perform an apt-get update."""
    if env is None:
        env = os.environ.copy()

    update_cmd = ["apt-get", "--quiet", "update"]

    with utils.Chroot(context, context.root) as chroot:
        chroot.run(update_cmd, env=env)


def run_apt_command(mode, context, packages=None, env=None):
    """Install, remove, or update all the packages using apt."""
    defopts = [
        "--assume-yes",
    ]
    if mode not in ["install", "remove", "update", "clean"]:
        die(f"{mode} not valid")

    if packages is None:
        packages = []

    if env is None:
        env = os.environ.copy()
        env["DEBIAN_FRONTEND"] = "noninteractive"

    cmd = ["apt-get"] + defopts + [mode] + packages
    with utils.Chroot(context, context.root) as chroot:
        chroot.run(cmd, env=env)
