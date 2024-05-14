---
title: Qemu image module
---

This module creates a qcow2 disk image. The module
is loaded by specifying "image.raw" in the manifest

```yaml
name: "Description of the task."
module: image.qemu
options: []
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
    * **name** (string): The name of the disk image.
    * **size** (string): The size of the disk image in GB.

The block device is configured by the disk parameter in the global parameters. It only
supports nbd block devices (ex: "/dev/nbd0")
