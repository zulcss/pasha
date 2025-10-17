# Installer ostree config module

This module configures OSTree repository settings.
This module is loaded by specifying the "installer.ostree.config" module.

```yaml
name: "Description of the task."
module: installer.ostree.config
options:
  repo_path: "/ostree/repo"
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
   * **repo_path** (string): Path to the OSTree repository.
