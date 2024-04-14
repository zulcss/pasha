"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import os
import shutil
import subprocess
import sys
from urllib.parse import urlparse

LOG = logging.getLogger(__name__)


def run_command(args, check=True, **kwargs):
    """Run a command in a shell."""
    LOG.debug("Running %s" % args)

    outputs = ""
    sp = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
        universal_newlines=True,
        **kwargs,
    )
    while True:
        output = sp.stdout.readline()
        if output:
            LOG.debug(output.rstrip("\n"))
            outputs += output
        if sp.poll() is not None:
            break

    # Read the remaining logs from stdout after process terminates
    output = sp.stdout.read()
    if output:
        LOG.debug(output.rstrip("\n"))
        outputs += output

    ret = sp.poll()

    if ret != 0:
        LOG.error(f"Failed to run command {args}\n{outputs}")
        if check:
            sys.exit(1)

    return ret, outputs.rstrip("\n")


def run_chroot_command(args, rootfs, efi=None, **kwargs):
    """Run bubblewarap in a seperate namespace."""
    cmd = [
        "bwrap",
        "--bind",
        rootfs,
        "/",
        "--ro-bind",
        "/etc/resolv.conf",
        "/etc/resolv.conf",
        "--proc",
        "/proc",
        "--dev-bind",
        "/dev",
        "/dev",
        "--bind",
        "/sys",
        "/sys",
        "--dir",
        "/run",
        "--bind",
        "/tmp",
        "/tmp",
        "--share-net",
        "--die-with-parent",
        "--chdir",
        "/",
    ]

    if efi:
        cmd += ["--bind", f"{efi}/efi", "/efi", "--bind", f"{efi}/efi", "/boot/efi"]

    cmd += args
    return run_command(cmd, **kwargs)


def fetch(source):
    a = urlparse(source)
    path = os.path.basename(a.path)

    LOG.info(f"Fetching from {source}.")
    run_command(["curl", source, "-o", path])
    return path


def which(cmd):
    return shutil.which(cmd)
