---
title: Raw image module
---

This module compresses a raw disk image. The module
is loaded by specifying "image.compress" in the manifest

```yaml
name: "Description of the task."
module: images.compress
options: []
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
    * **name** (string): The name of the disk image.
    * **compression** (string): The compressor: gzip or xz

The block device is configured by the disk parameter in the global parameters. It only
supports loop back block devices (ex: "/dev/loop0")
