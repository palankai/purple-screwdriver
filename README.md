# purple-screwdriver
Odoo deployment tool (addon)

This module ensure an up-to-date state of modules. As a developer you don't
have to worry any manual deployment steps anymore.
You have to provide a list of modules that should be installed or remove
an already installed module from the config file in order of uninstall.

## Decision matrix

| Expected status | Status      | Condition             | Action     |
|:---------------:|:-----------:| --------------------- |:----------:|
| removed         | installed   |                       | uninstall  |
| removed         | uninstalled |                       | do nothing |
| installed       | uninstalled |                       | install    |
| installed       | installed   |                       | do nothing |
| installed       | installed   | ver Avail != ver Inst | upgrade    |
| upgraded        | uninstalled |                       | install    |
| upgraded        | installed   |                       | upgrade    |


## Usage

```bash
    $ odoo.py screwdriver -d <database name> -c <screwdriver config>
```

## Config file

Yaml configuration. The file should have an entry called addons which
should be a mapping between name of modules and expected state (as above).
The module name is the the internal name (like 'sales' instead of 'Sales...').

### Example

```yaml
---
addons:
    sales: installed
    hr: updated
    purchase: removed
```

