# BootOrder module

This module sets EFI boot order. The module
is loaded by specifying "utils.bootorder" in the manifest.

```yaml
name: "Description of the task."
module: utils.bootorder
options: []
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
