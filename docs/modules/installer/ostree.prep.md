---
title: ostree prep module
---

This module transforms a rootfs tarball into a deployable ostree branch.
This module is loaded by specifying the "installer.ostree.prep" module.


```yaml
name: "Description of the task."
module: installer.ostree.prep
options:
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.

There are no specific options for this module since the parameters are passed
through the params configuration.
