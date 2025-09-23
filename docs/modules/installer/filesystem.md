---
title: Installer filesystem module
---

This module creates file systems on created partitions. This module is loaded
by specifying the "installer.disk.fs".

```yaml
name: "Description of the task."
module: installer.disk.fs
options:
  filesystem:
    - name: EFI
      label: EFI
      fs: vfat
      options: []
    - name: ROOT
      label: ROOT
      fs: ext4
      options: []
```      

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object):
    **filesystems** (list):
       * **name** (string): The name is used for referencing the named partition
         that was created.
       * **label** (string): The label is the label for the file system that will be
         created.
       * **fs** (string): The type of file system to be created.
       * **options** (string): Additional file system options that can be used while
         creating the file system.
