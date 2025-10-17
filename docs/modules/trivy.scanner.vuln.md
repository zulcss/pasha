# Trivy vulnerability scanner module

This module runs Trivy vulnerability scanner on the image.
This module is loaded by specifying the "trivy.scanner.vuln" module.

```yaml
name: "Description of the task."
module: trivy.scanner.vuln
options:
  format: "json"
  output: "vulnerabilities.json"
```

* **name** (string): Description of the task.
* **module** (string): The name of the module to load.
* **options** (object): Optional options to pass to the module.
   * **format** (string): Output format (json, table, sarif).
   * **output** (string): Output file path.
