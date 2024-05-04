---
title: Installer unpack module
---

This module unpacks a rootfs tarball for the installer (tiler). This
module is loaded by specifying the "installer.unpack" module in the manifest.

```yaml
name: "Description of the task."
module: installer.unpack
options:
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object)

There are no options to pass the module, however the global parameters (params)
must specify the disk and tarball to be unpacked. 
