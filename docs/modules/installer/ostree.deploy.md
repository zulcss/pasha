# ostree deploy module

This module deploys an ostree branch onto a block device. This module is loaded
by specifying the "installer.ostree.deploy" module

```yaml
name: "Description of the task."
module: installer.ostree.deploy
options:
  kernel_args:
        * root=LABEL=ROOT
        * rw
        * console=tty0
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
   * **kernel_args** Kernel command line configuration to deploy with the branch
     to make the block device bootable.
