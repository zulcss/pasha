# Container build module

This module inserts a directory containing the rootfs tarball into an OCI
container. The source tarball to create the container from must be specified
in the manifest's parameters.

```yaml
name: "Description of the task."
module: container.build
options:
  image: "myimage:latest"
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
   * **image** (string) The container image to be created.
