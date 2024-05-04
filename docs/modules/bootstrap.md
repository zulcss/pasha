---
title: bootstrap module
---

This module unpacks a rootfs tarball or squashfs image. The module
is loaded by specifying "bootstrap.mmdestrap" in the manifest.

```yaml
name: "Description of the task."
module: bootstrap.mmdebstrap
options: []
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
     * **target** (string) The rootfs tarball to be created.
     * **suite** (string) The Debian release to install. Valid versions are:
            - bookworm
            - trixie
            - testing
            - sid
    * **packages** (list) Extra packages to install into the rootfs
    * **mirrors** (list) Extra Debian package mirrors to use.
    * **customize_hooks** (list) Commands to run after the rootfs is created.
    * **components** (list) Extra pockets to use in sources.list.
    * **variant** (string) Type of Debian image to install. Please see mmdebstrap
       man page for an explanation.
    * **hooks** (list) Additional script to run during bootstrapping. Please see
      mmdebstrap man page for an explanation.
    * **setup_hooks** (list) Commands to run before bootstrapping takes place. Please
      see mmdebstrap man page for an explanation.
    * **essential_hooks** (list) Commands to to run after the "Essential: yes" packages have
      beeen installed. Please see mmdebstrap man page for an explanation.
    * **apt_hooks** (list) Extra configuration hooks for apt.
    * **mode** (string) Run specific mmdebstrap mode.
    * **keyring** (list) Additional gpg keys to install.
    * **dpkg_opts** (list) Extra dpkg configuration options.
    * **format** (string) rootfs artifact format. 
