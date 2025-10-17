# Installer ostree commit module

This module commits changes to an OSTree repository.
This module is loaded by specifying the "installer.ostree.commit" module.

```yaml
name: "Description of the task."
module: installer.ostree.commit
options:
  branch: "main"
  subject: "Commit message"
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
   * **branch** (string): The branch to commit to.
   * **subject** (string): Commit message.
