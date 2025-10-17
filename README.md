# Pasha - Debian OS Build Modules

Pasha is a modular framework for building Debian-based OS images and
containers. It provides a collection of modules that can be orchestrated to
create custom Linux distributions, container images, and installer media.

## Features

* **Modular Architecture**: Extensible plugin system for custom build steps
* **Multiple Image Types**: Support for raw disk images, compressed images, and containers
* **Debian Integration**: Native support for Debian package management and bootstrapping
* **OSTree Support**: Full OSTree integration for immutable OS deployments
* **Security Scanning**: Built-in Trivy vulnerability scanning
* **Flexible Configuration**: YAML-based manifest system

## Installation

Please use installation instructions found in the Rucksack or Tiler projects.
The following installation instructions are only provided to assist in
configuring a standalone development environment for Pasha.

Install from source:

```bash
git clone https://gitlab.com/elxr/tools/pasha.git
cd pasha
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r test-requirements.txt
pip install -r ci-requirements.txt
pip install -e .
```

## Available Modules

### Bootstrap & Packaging

* `bootstrap.mmdebstrap` - Create Debian rootfs using mmdebstrap
* `apt.update` - Update package lists
* `apt.install` - Install packages
* `apt.remove` - Remove packages

### Image Creation

* `image.raw` - Create raw disk images
* `image.compress` - Compress disk images (gzip, xz, zstd)
* `image.repart` - Partition images using systemd-repart

### Container Support

* `container.build` - Build OCI containers

### File Operations

* `unpack.tarball` - Extract tarballs
* `utils.copy` - Copy files between host and target
* `utils.user` - Create users in the target system

### System Utilities

* `utils.run_command` - Execute commands in target
* `utils.run_shell` - Interactive shell access
* `utils.bootorder` - Configure EFI boot order

### Installer Modules

* `installer.disk.parted` - Partition disks
* `installer.disk.fs` - Create filesystems
* `installer.bootloader` - Install bootloaders
* `installer.bootloader.grub` - GRUB bootloader
* `installer.bootloader.ostree` - OSTree bootloader

### OSTree Integration

* `installer.ostree.init` - Initialize OSTree repository
* `installer.ostree.commit` - Commit to OSTree
* `installer.ostree.deploy` - Deploy OSTree commits
* `installer.ostree.pull.local` - Pull from local repository
* `installer.ostree.pull.remote` - Pull from remote repository

### Security

* `trivy.scanner.vuln` - Vulnerability scanning with Trivy

## Configuration

Pasha uses YAML manifests to define build tasks. Each task specifies:

* `name`: Human-readable description
* `module`: Module to execute
* `options`: Module-specific parameters

Example manifest structure:

```yaml
parameters:
  disk: "/dev/loop0"
  target: "/tmp/build"

tasks:
        * name: "Task description"
    module: module.name
    options:
      param1: value1
      param2: value2
```

## Development

To add a new module:

1. Copy `pasha/modules/noop.py` as a template
1. Implement your module class
1. Add entry point in `setup.py` under `pasha.modules`
1. Create documentation in `docs/modules/`

Testing and Code Quality:

```bash
# Run all tests and checks
tox

# Run specific checks
tox -e pep8        # Code style and formatting
```

Manual testing:

```bash
python -m pytest
```

## License

Licensed under the Apache License, Version 2.0. See LICENSE file for details.

## Contributing

Contributions are welcome! Please ensure:

* Code follows PEP 8 style guidelines
* Tests are included for new functionality
* Documentation is updated for new modules
* Commit messages are descriptive

### Branch Guidelines

* Send changes to the `main` branch **unless** it is a bug fix that only applies
  to a specific release branch
* Merge requests to port bug fixes from `main` to release branches should be
  sent after a bug fix is merged to `main`
* Minor releases should only include bug fixes
* Major releases will include bug fixes and new features
