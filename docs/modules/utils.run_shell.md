---
title: Run shell module
---

This module runs a shell on the image during the build process. 
The module is loaded by specifying "utils.run_shell" in the manifest.

```yaml
name: "Description of the task."
module: utils.run_shell
options: []
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
    * **commands** (list): Commands to run during the build. 
