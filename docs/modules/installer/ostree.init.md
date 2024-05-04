---
title: ostree init module
---

This module creates an empty ostree repository. This module is loaded
by specifying the "installer.ostree.init" module


```yaml
name: "Description of the task."
module: installer.ostree.init
options:
  mode: archive-z2
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
    * **mode** Initialize the repository in a given mode. Valid modes are the
    following:
       - bare
       - bare-user
       - bare-user-only
       - archive-mode-z2
