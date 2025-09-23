---
title: systemd-repart module
---

This module creates a raw ddi based image. This module is loaded
by specifying "image.repart" in the manifest.

```yaml
name: "Description of the task."
module: images.repart
options: []
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (string): Optional options to pass to the module.
   * **root** (string):  The size of the root partition in Gigabytes
   * **esp** (string): The size of the ESP partition in Mega/Giga bytes,
                       the minimum size is 512MB, otherwise the image will 
                       not boot.
   * **definitions** (string): The path to the systemd-repart definition files.
                     For configuration file format please see repart.d(5).
