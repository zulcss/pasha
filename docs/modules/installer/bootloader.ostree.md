---
title: Installer ostree bootloader module
---

This module will run bootctl to install the bootloader on a block device.
After the bootloader is installed it will move the kernel and ramdisk
into the correct directories, This module is loaded by specifying
the "installer.bootloader" module.

```yaml
name: "Description of the task."
module: installer.bootloader
options:
  kernel_args: "root=LABEL=ROOT console=tty0 console=ttyS0,115200"
  uefi_driver: ext4
```  

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object):
    * **kernel_args** (string) Sets the /proc/cmdline values to boot a kernel.
    * **uefi_driver** (string) The uefi driver to load while setting up 
      the bootloader. 
  
