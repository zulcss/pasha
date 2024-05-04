---
title: Run command module
---

This module runs a command on the image during the build process. 
The module is loaded by specifying "utils.run_command" in the manifest.

# yaml syntax
name: "Description of the task."
module: utils.run_command
options: []

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
    * **commands** (list): Commands to run during the build. 
