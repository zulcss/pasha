"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

from unittest import mock

from pasha import archive, exceptions, utils
from pasha.tests import base


class TestArchive(base.TestCase):
    def test_archive(self):
        with mock.patch.object(utils, "run_command") as execute:
            execute.return_value = (0, "fake_output")
            archive.unpack("fake_archive", "fake_rootfs")
            execute.assert_called_once_with(
                [
                    "tar",
                    "-C",
                    "fake_rootfs",
                    "--exclude=./dev/*",
                    "-zxf",
                    "fake_archive",
                    "--numeric-owner",
                ]
            )
