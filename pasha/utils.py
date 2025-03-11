"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import os
import shutil
import subprocess
import sys
from urllib.parse import urlparse

from pasha.log import complete_step, die

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


class Chroot(object):
    """Run a command in a chrootable target."""

    def __init__(self, context, root):
        self.context = context
        self.root = root

        self.cmd = ["bwrap", "--bind", self.root, "/"]

        # vfs mounts
        self.cmd += ["--proc", "/proc"]
        self.cmd += ["--dev-bind", "/dev", "/dev"]
        self.cmd += ["--bind", "/sys", "/sys"]

        # fs mounts
        self.cmd += ["--dir", "/run"]

        # bwrap args
        self.cmd += ["--share-net"]
        self.cmd += ["--die-with-parent"]
        self.cmd += ["--chdir", "/"]

    def __enter__(self):
        with complete_step("Setting up chroot target"):
            resolv = self.root.joinpath("etc/resolv.conf")
            if resolv.exists() or resolv.is_symlink():
                # Use the host's /etc/resolv.conf
                os.rename(resolv, self.root.joinpath("etc/resolv.conf.bak"))
                self.cmd += ["--bind", "/etc/resolv.conf", "/etc/resolv.conf"]

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        with complete_step("Tearing down chroot target"):
            resolv = self.root.joinpath("etc/resolv.conf.bak")
            if resolv.exists() or resolv.is_symlink():
                os.rename(resolv, self.root.joinpath("etc/resolv.conf"))

    def run(self, args, **kwargs):
        """Run a command im a chrootable environment"""
        try:
            LOG.debug(f"Running {subprocess.list2cmdline(args)}.")
            subprocess.run(self.cmd + args, check=True, **kwargs)
        except subprocess.CalledProcessError as e:
            die(f"Failed to run command: " + e.stderr.decode("utf-8").strip())


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
