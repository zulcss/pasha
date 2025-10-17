---
title: Installer grub bootloader module
---

This module will install GRUB bootloader on a block device.
This module is loaded by specifying the "installer.bootloader.grub" module.

```yaml
name: "Description of the task."
module: installer.bootloader.grub
options:
  kernel_args: "root=LABEL=ROOT console=tty0 console=ttyS0,115200"
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
    * **kernel_args** (string): Kernel command line arguments.
