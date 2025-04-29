# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# THIS FILE IS MANAGED BY THE GLOBAL REQUIREMENTS REPO - DO NOT EDIT


try:
    from setuptools import find_packages, setup
except ImportError:
    sys.exit("setuptools is required.")

from pasha import __version__ as pasha_version

with open("README.rst", "r", encoding="utf-8") as f:
    long_description = f.read()


# Parse requirements
with open("requirements.txt") as requires:
    install_requires = requires.read().splitlines()

setup(
    name="pasha",
    version=pasha_version,
    author="Chuck Short",
    author_email="charles.short@windriver.com",
    description="Library to help manage ruck and tiler.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://gitlab.com/elxr/tools/pasha.git",
    python_requires=">=3.6",
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        "pasha.modules": [
            # noop module
            "noop.placeholder = pasha.modules.noop:Noop",
            # installer modules
            "installer.disk.parted = pasha.modules.installer.disk:Parted",
            "installer.disk.fs = pasha.modules.installer.disk:Filesystem",
            "installer.unpack = pasha.modules.installer.unpack:Unpack",
            "installer.bootloader = pasha.modules.installer.bootloader:Bootloader",
            "installer.bootloader.ostree = "
            "pasha.modules.installer.bootloader:BootloaderOstree",
            "installer.bootloader.grub = "
            "pasha.modules.installer.bootloader:BootloaderGrub",
            "installer.ostree.init = pasha.modules.installer.ostree:OstreeInit",
            "installer.ostree.pull.local = "
            "pasha.modules.installer.ostree:OstreePullLocal",
            "installer.ostree.pull.remote = "
            "pasha.modules.installer.ostree:OstreePullRemote",
            "installer.ostree.deploy = pasha.modules.installer.ostree:OstreeDeploy",
            "installer.ostree.prep = pasha.modules.installer.ostree:OstreePrep",
            "installer.ostree.config = pasha.modules.installer.ostree:OstreeConfig",
            "installer.ostree.commit = pasha.modules.installer.ostree:OstreeCommit",
            # bootstrap modules
            "bootstrap.mmdebstrap = pasha.modules.bootstrap:Bootstrap",
            # unpack module
            "unpack.tarball = pasha.modules.unpack:Unpack",
            # container modules
            "container.build = pasha.modules.container:Container",
            # images modules
            "image.raw = pasha.modules.images.raw:RawImage",
            "image.compress = pasha.modules.images.compress:CompressImage",
            "image.repart = pasha.modules.images.repart:RepartImage",
            # utils modules
            "utils.run_command = pasha.modules.cmd:Command",
            "utils.run_shell = pasha.modules.cmd:ShellCommand",
            "utils.user = pasha.modules.user:User",
            "utils.copy = pasha.modules.copy:Copy",
            "utils.bootorder = pasha.modules.bootorder:BootOrder",
            # apt modules
            "apt.update = pasha.modules.apt:AptUpdate",
            "apt.install = pasha.modules.apt:AptInstall",
            "apt.remove = pasha.modules.apt:AptRemove",
            # security modules
            "trivy.scanner.vuln = pasha.modules.security.trivy:TrivyVulnScan",
        ]
    },
)
