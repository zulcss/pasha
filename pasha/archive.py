"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import os
import shlex
import subprocess

from pasha.log import die


def unpack(archive, rootfs):
    """Unpack a tarball."""
    try:
        subprocess.run(
            [
                "tar",
                "-C",
                rootfs,
                "--exclude=./dev/*",
                "-zxf",
                archive,
                "--numeric-owner",
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        die(f"Failed to unpack {archive}: " + e.stderr.decode("utf-8").strip())


def compress(archive, compressor="zstd"):
    """Compress image by using the desired archive program."""
    if not os.path.exists(archive):
        die(f"{archive} not found.")

    ncpu = os.cpu_count()
    if compressor == "xz":
        cmd = f"xz -9 -T{ncpu} -f --keep {archive}"
    elif compressor == "gzip":
        cmd = f"gzip -1 --keep -f {archive}"
    elif compressor == "zstd":
        cmd = f"zstd -3 --keep -f -T{ncpu} {archive}"
    else:
        die(f"{compressor} not supported")

    try:
        subprocess.run(shlex.split(cmd), check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        die(f"Failed to compress {archive}: " + e.stderr.decode("utf-8").strip())
    except FileNotFoundError:
        die(f"{cmd.split()[0]} is not found.")
