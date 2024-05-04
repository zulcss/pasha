---
title: Installer bootloader module
---

This module will run bootctl to install the boot loader on a block device. This module
is loaded by specifying the "installer.bootloader" module.

```yaml
name: "Description of the task."
module: installer.bootloader
options:
  kernel_args: "root=LABEL=ROOT console=tty0 console=ttyS0,115200"
  uefi_driver: ext4
```  

* **name** (string): Description of the task.
* **module** (string) The name of the module to load.
* **options** (object):
    * **kernel_args** (string): Sets the /proc/cmdline values to book a kernel.
    * **uefi_driver** (string): The uefi driver to load while setting up 
      the bootloader. 
  
