# apt install module

This module run apt-get install on the image. The module
is loaded by specifying "apt.install" in the manifest.

```yaml
name: "Description of the task."
module: apt.install
options:
  packages:
        * foo
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
