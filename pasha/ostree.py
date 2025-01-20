"""
Copyright (c) 2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import subprocess

from pasha.log import die


def cli(*args, **kwargs):
    """Wrapper for the ostree command."""
    args = list(args) + [f"--{k}={v}" for k, v in kwargs.items()]
    try:
        subprocess.run(
            ["ostree"] + args,
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        die(f"Ostree command failed: " + e.stderr.decode("utf-8").strip())


def ostree_ref(repo, branch):
    """Resolve the revision given a branch."""
    r = subprocess.run(
        ["ostree", "rev-parse", f"--repo={repo}", branch],
        encoding="utf8",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    msg = r.stdout.strip()
    if r.returncode != 0:
        die(f"Failed to find revision for {branch}")

    return msg
