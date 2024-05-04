---
title: Undeploy module
---

This module unmounts a block device onto the temporary rootfs mount point. The module
is loaded by specifying "utils.undeploy" in the manifest.

```yaml
name: "Description of the task."
module: utils.undeploy
options: []
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
