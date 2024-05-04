---
title: Installer Parted module
---

This module uses parted to create partitions. This module is loaded by
specifying the "installer.disk.parted" module.

```yaml
name: "Description of the task."
module: installer.disk.parted
options:
  slices:
    - name: EFI
      start: 0%
      end: 128MB
      flags: [boot, esp]
      id: c12a7328-f81f-11d2-ba4b-00a0c93ec93b
    - name: ROOT
      start: 128MB
      end: 100%
      flags: []
      id: ''
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object):
    * **slices**
        * **name** (string): The name is used for referencing named 
          partition for mount points and the label for the file system 
          located on this partition. Must be unique.
        * **start** (string): The offset from the beginning on the disk
          there the partition starts
        * **end** (string): The offset from the beginning on the disk, 
          there the partition ends.
        * **flags** (string): The list of the additional flags for the 
          partition compatible with parted(8).
        * **id** (string): The ID of the partition defined by UUIDs based
          on GUID Partition types. Based on 
          https://en.wikipedia.org/wiki/GUID_Partition_Table
