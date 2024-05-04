---
title: Deploy module
---

This module mounts a block device onto the temporary rootfs mount point. The module
is loaded by specifying "utils.deploy" in the manifest.

```yaml
name: "Description of the task."
module: utils.deploy
options: []
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
