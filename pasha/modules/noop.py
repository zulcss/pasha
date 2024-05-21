"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging

from pasha.modules.base import ModuleBase


class Noop(ModuleBase):
    """Module that does nothing."""

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.state = stage

        self.logging = logging.getLogger(__name__)

    def run(self):
        self.logging.info("hello world")

    def validate(self):
        pass
