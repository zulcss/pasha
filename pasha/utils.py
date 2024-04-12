"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import os
import shutil
import subprocess
from urllib.parse import urlparse

LOG = logging.getLogger(__name__)


def run_command(args, data=None, env=None, capture=False, shell=False, **kwargs):
    LOG.debug("Running %s" % args)

    try:
        if not capture:
            stdout = None
            stderr = None
        else:
            stdout = subprocess.PIPE
            stderr = subprocess.PIP
        stdin = subprocess.PIPE
        sp = subprocess.Popen(args, stdout=stdout, stderr=stderr, stdin=stdin, **kwargs)
        (out, err) = sp.communicate(data)
    except OSError:
        try:
            out = out.decode("utf-8") if out else ""
            err = err.decode("utf-8") if err else ""
            raise Exception(f"Failed to run command {args}, out={out}, error={err}")
        except UnboundLocalError:
            raise Exception(args)
    return (out, err)


def run_chroot_command(
    args, rootfs, efi=None, data=None, env=None, capture=None, shell=False, **kwargs
):
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
    return run_command(cmd, data=None, env=None, capture=capture, shell=shell)


def fetch(source):
    a = urlparse(source)
    path = os.path.basename(a.path)

    LOG.info(f"Fetching from {source}.")
    run_command(["curl", source, "-o", path])
    return path


def which(cmd):
    return shutil.which(cmd)
