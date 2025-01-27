"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import pathlib
import tempfile
from unittest import mock

from omegaconf import OmegaConf

from pasha.modules.installer import bootloader
from pasha.tests import base


class TestSDBootloader(base.TestCase):
    def setUp(self):
        super(TestSDBootloader, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.config = OmegaConf.create(
            {
                "name": "fake_name",
                "architecture": "amd64",
                "params": {
                    "disk": "fake_image.img",
                },
            }
        )
        self.stage = OmegaConf.create({"kernel_args": "fake_kernel_args"})

    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    @mock.patch("pasha.bootloader.install_systemd_boot")
    @mock.patch("os.path.exists")
    def test_sd_bootloader(self, mock_exists, mock_bootloader, mock_which, mock_run):
        rootfs = self.tempdir.joinpath("fake_name/rootfs")
        expected_calls = [
            mock.call(
                ["systemd-dissect", "--mount", "--mkdir", "fake_image.img", rootfs],
                check=True,
                capture_output=True,
            ),
            mock.call(
                [
                    "bootctl",
                    "install",
                    f"--root={rootfs}",
                    "--no-variables",
                    "--entry-token",
                    "os-id",
                ],
                check=True,
                capture_output=True,
            ),
            mock.call(
                ["systemd-dissect", "--umount", rootfs], capture_output=True, check=True
            ),
        ]
        bootloader.Bootloader(self.state, self.config, self.stage).run()
        self.assertEqual(mock_run.call_args_list, expected_calls)


class TestGrubBootloader(base.TestCase):
    def setUp(self):
        super(TestGrubBootloader, self).setUp()
        self.state = mock.MagicMock()
        self.tempdir = pathlib.Path(tempfile.mkdtemp())
        self.state.workspace = self.tempdir
        self.config = OmegaConf.create(
            {
                "name": "fake_name",
                "architecture": "amd64",
                "params": {
                    "image": "fake_image.img",
                    "disk": "/dev/sda",
                },
            }
        )
        self.stage = OmegaConf.create({})

    @mock.patch("os.path.exists")
    @mock.patch("subprocess.run")
    @mock.patch("json.loads")
    def test_grub_bootloader_x86(self, mock_json, mock_run, mock_os):
        rootfs = self.state.workspace.joinpath("fake_name/rootfs")
        mock_os.return_value = True
        expected_calls = [
            mock.call(
                ["systemd-dissect", "--json", "pretty", "/dev/sda"],
                check=True,
                capture_output=True,
                encoding="utf8",
            ),
            mock.call(
                ["mount", "-o", "bind", "/dev", str(rootfs.joinpath("dev"))], check=True
            ),
            mock.call(
                ["mount", "-o", "bind", "/proc", str(rootfs.joinpath("proc"))],
                check=True,
            ),
            mock.call(
                ["mount", "-o", "bind", "/sys", str(rootfs.joinpath("sys"))], check=True
            ),
            mock.call(["chroot", rootfs, "update-grub"]),
            mock.call(
                [
                    "chroot",
                    rootfs,
                    "grub-install",
                    "--uefi-secure-boot",
                    "--efi-directory=/efi",
                    "--target=x86_64-efi",
                    "--no-nvram",
                    "--removable",
                ],
                check=True,
            ),
            mock.call(["umount", rootfs.joinpath("sys")], check=False),
            mock.call(["umount", rootfs.joinpath("proc")], check=False),
            mock.call(["umount", rootfs.joinpath("dev")], check=False),
        ]
        bootloader.BootloaderGrub(self.state, self.config, self.stage).run()
        self.assertEqual(mock_run.call_args_list, expected_calls)

    @mock.patch("os.path.exists")
    @mock.patch("subprocess.run")
    @mock.patch("json.loads")
    def test_grub_bootloader_arm64(self, mock_json, mock_run, mock_os):
        self.config = OmegaConf.create(
            {
                "name": "fake_name",
                "architecture": "arm64",
                "params": {
                    "disk": "/dev/sda",
                },
            }
        )
        self.stage = OmegaConf.create({})
        rootfs = self.state.workspace.joinpath("fake_name/rootfs")
        mock_os.return_value = True
        expected_calls = [
            mock.call(
                ["systemd-dissect", "--json", "pretty", "/dev/sda"],
                check=True,
                capture_output=True,
                encoding="utf8",
            ),
            mock.call(
                ["mount", "-o", "bind", "/dev", str(rootfs.joinpath("dev"))], check=True
            ),
            mock.call(
                ["mount", "-o", "bind", "/proc", str(rootfs.joinpath("proc"))],
                check=True,
            ),
            mock.call(
                ["mount", "-o", "bind", "/sys", str(rootfs.joinpath("sys"))], check=True
            ),
            mock.call(["chroot", rootfs, "update-grub"]),
            mock.call(
                [
                    "chroot",
                    rootfs,
                    "grub-install",
                    "--uefi-secure-boot",
                    "--efi-directory=/efi",
                    "--target=arm64-efi",
                    "--no-nvram",
                    "--removable",
                ],
                check=True,
            ),
            mock.call(["umount", rootfs.joinpath("sys")], check=False),
            mock.call(["umount", rootfs.joinpath("proc")], check=False),
            mock.call(["umount", rootfs.joinpath("dev")], check=False),
        ]
        bootloader.BootloaderGrub(self.state, self.config, self.stage).run()
        self.assertEqual(mock_run.call_args_list, expected_calls)
