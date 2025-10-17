# apt update module

This module run apt-get update on the image. The module
is loaded by specifying "apt.update" in the manifest.

```yaml
name: "Description of the task."
module: apt.update
options: []
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
