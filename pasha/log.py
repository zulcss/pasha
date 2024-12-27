"""
Copyright (c) 2024-2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import contextlib
import logging
import sys


@contextlib.contextmanager
def complete_step(text, text2=None):
    """Pass a message to the user when a step is happening and
    when it ends.
    """
    print_step(text + "...")
    args = []
    yield args
    if text2 is None:
        text2 = text + " complete"
    print_step(text2.format(*args) + ".")


def print_step(text):
    """Display some text to the logging subsystem."""
    logging.info(f"{text}")


def die(msg, hint=None):
    """Print a message to the user and terminate.
    Hint to the user why rucksack/pasha is being terminated
    """
    logging.error(msg)
    if hint:
        logging.info(hint)
    sys.exit(1)
