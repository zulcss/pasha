# unpack module

This module unpacks a rootfs tarball or squashfs image. The module
is loaded by specifying "unpack.tarball" in the manifest.

```yaml
name: "Description of the task."
module: unpack.tarball
options: []
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
   * **sources** (list): A list of sources to unpack.
