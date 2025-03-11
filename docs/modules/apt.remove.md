---
title: apt remove module
---

This module run apt-get remove on the image. The module
is loaded by specifying "apt.remove" in the manifest.

```yaml
name: "Description of the task."
module: apt.remove
options:
  packages:
    - foo
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
      **packages** (list): Package to remove
