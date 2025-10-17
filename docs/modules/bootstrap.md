# bootstrap module

This module unpacks a rootfs tarball or squashfs image. The module
is loaded by specifying "bootstrap.mmdebstrap" in the manifest.

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
      * bookworm
      * trixie
      * testing
      * sid
      * aria
   * **packages** (list) Extra packages to install into the rootfs
   * **mirrors** (list) Extra Debian package mirrors to use.
   * **customize_hooks** (list) Commands to run after the rootfs is created.
   * **components** (list) Extra pockets to use in sources.list.
   * **variant** (string) Type of Debian package set to install. Please see mmdebstrap
     man page for an explanation.
   * **hooks** (list) Additional script to run during bootstrapping in a directory.
     Please see mmdebstrap man page for an explanation.
   * **setup_hooks** (list) Execute arbitrary command right after initial
     setup. Please see mmdebstrap man page for an explanation.
      * **essential_hooks** (list) Commands to run after the "Essential: yes"
        packages have been installed. Please see mmdebstrap man page for an
        explanation.
   * **extract_hooks** (list) Commands to run after the essential packages are
     installed. Please see mmdebstrap man page for an explanation.
   * **apt_hooks** (list) Extra configuration for apt which will be
     permanently added. Please see the man page.
   * **mode** (string) Run specific mmdebstrap mode.
   * **keyring** (list) Additional gpg keys to install.
   * **dpkg_opts** (list) Extra dpkg configuration options.
   * **format** (string) rootfs artifact format.
   * **cache_proxy** (string) HTTP proxy for package caching
     (e.g., "<http://localhost:3142"> for apt-cacher-ng).
