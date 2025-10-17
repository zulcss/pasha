# ostree pull remote module

This module pulls commits from a remote module. This module is loaded
by specifying the "installer.ostree.pull.remote" module.

```yaml
name: "Description of the task."
module: installer.ostree.pull.remote
options:
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.

There are no specific options for this module since the parameters are passed
through the params configuration.
