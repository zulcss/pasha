# Copy module

Copy a file or directory from the host to the target image or container

```yaml
name: "Description of the task"
module: utils.copy
options:
  source: foo
  dest: bar
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load (utils.copy)
* **options** (object): Options to pass to the utils.copy module
   * **source**: (list) The path to copy the file from.
   * **dest**: (list) The path to copy the file to.
