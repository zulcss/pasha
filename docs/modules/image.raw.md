---
title: Raw image module
---

This module creates a raw disk image. The module
is loaded by specifying "image.raw" in the manifest

```yaml
name: "Description of the task."
module: images.raw
options:
  name: "disk.img"
  size: "20G"
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
    * **name** (string): The name of the disk image.
    * **size** (string): The size of the disk image in GB.

The block device is configured by the disk parameter in the global parameters. It only
supports loop back block devices (ex: "/dev/loop0")
