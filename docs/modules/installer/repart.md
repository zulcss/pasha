# Installer reparted module

This module uses systemd-repart to create partitions and file system.
This module is loaded by specifying "installer.disk.repart" module.

```yaml
name: "Description of the task."
module: installer.disk.repart
options:
  size: 20G
  definitions: disks/
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load
* **options** (object):
        * **size** (string): The size of the disk to be created
        * **definitions** (string) The directory of the systemd-repart
          configuration files. See repart.d(5) for configuration options.
