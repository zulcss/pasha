# ostree pull local module

This module pulls commits from one repository into another. This module is
loaded
by specifying the "installer.ostree.pull.local" module.

```yaml
name: "Description of the task."
module: installer.ostree.pull.local
options:
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.

There are no specific options for this module since the parameters are passed
through the params configuration.
