"""
Copyright (c) 2025 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import shutil
import subprocess

from pasha.context import Context
from pasha.log import complete_step, die
from pasha.modules.base import ModuleBase
from pasha.mount import mount_disk


class TrivyVulnScan(ModuleBase):
    """Run trivy to scan an image."""

    def __init__(self, state, config, stage):
        self.state = state
        self.config = config
        self.stage = stage

        if not shutil.which("trivy"):
            die("Trivy binary is not installed.")

        self.context = Context(self.state, self.config, self.stage)

    def run(self):
        with complete_step("Running trivy vulnerability scanner"):
            with mount_disk(self.context.params.disk, self.context.root):
                logfile = self.context.staging.joinpath("cve_scan_result.txt")
                logging.info("Running trivy scanner.")

                try:
                    subprocess.run(
                        [
                            "trivy",
                            "rootfs",
                            "--output",
                            logfile,
                            "--scanners",
                            "vuln",
                            self.context.root,
                        ],
                        check=True,
                    )
                except subprocess.CalledProcessError as error:
                    logging.error("Failed to run trivy: {error}")
