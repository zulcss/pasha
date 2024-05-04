---
title: Noop module
---

This module is a place holder to ensure that pasha is being loaded correctly.
The module can be used as a template to create more modules from. The module
is loaded by specifying "noop.placeholder" in the manifest.

```yaml
name: "Description of the task."
module: noop.placeholder
options: []
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
