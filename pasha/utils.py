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


def run_command(args, **kwargs):
    """Run a command in a shell."""
    LOG.debug("Running %s" % format_command(args))

    outputs = ""
    try:
        sp = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            universal_newlines=True,
            **kwargs,
        )
    except FileNotFoundError:
        msg = f"You do not have {args[0]} installed."
        LOG.error(msg)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        args = format_command(args)
        msg = (
            f"Running the following command {args} resulted in a non-zero return code: "
        )
        msg += f"{e.returncode}"
        LOG.error(msg)
        LOG.error("'stdout': ")
        LOG.error(e.stdout)
        LOG.error("'stderr': ")
        LOG.error(e.stderr)
        sys.exit(1)
    except Exception as e:
        msg = f"Error running the following command {format_command(args)}: {e}"
        LOG.error(msg)
        sys.exit(1)

    while True:
        output = sp.stdout.readline()
        if output:
            LOG.debug(output.rstrip("\n"))
            outputs += output
        if sp.poll() is not None:
            break

    # Read the remaining logs from stdout after process terminates
    ret = sp.poll()
    output = sp.stdout.read()
    if output:
        LOG.debug(output.rstrip("\n"))
        outputs += output

    return ret, outputs.rstrip("\n")


def run_chroot_command(args, rootfs, efi=None, boot=None, **kwargs):
    """Run bubblewarap in a new namespace."""
    cmd = [
        "bwrap",
        "--bind",
        rootfs,
        "/",
        "--proc",
        "/proc",
        "--dev-bind",
        "/dev",
        "/dev",
        "--dir",
        "/run",
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

    if boot:
        cmd += ["--bind", f"{boot}/boot", "/boot"]

    if efi:
        cmd += ["--bind", f"{efi}/efi", "/efi"]

    cmd += args
    return run_command(cmd, **kwargs)


def fetch(source):
    """Fetch a file from a specific site."""
    a = urlparse(source)
    path = os.path.basename(a.path)

    LOG.info(f"Fetching from {source}.")
    run_command(["curl", source, "-o", path])
    return path


def which(cmd):
    return shutil.which(cmd)


def format_command(args):
    """Format command string for pretty printing."""
    if isinstance(args, list):
        return subprocess.list2cmdline(args)
