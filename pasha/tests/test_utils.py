"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import subprocess
from unittest import mock

import pytest

from pasha import utils
from pasha.tests import base


class TestUtils(base.TestCase):
    def test_run_command(self):
        with mock.patch.object(subprocess, "Popen") as execute:
            utils.run_command(["ls", "foo"])
            execute.assert_called_once_with(
                ["ls", "foo"], stdout=-1, stderr=-2, stdin=-1, universal_newlines=True
            )

    def test_run_command_not_found(self):
        with pytest.raises(SystemExit) as err:
            utils.run_command(["foo"])
