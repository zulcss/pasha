"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""


class PashaError(Exception):
    """Base class for pasha exceptions."""

    def __init__(self, message=None):
        super(PashaError, self).__init__(message)
        self.message = message

    def __str__(self):
        return self.message or ""


class ConfigError(PashaError):
    """Pasha cofiguration error."""
    pass
