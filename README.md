# purple-screwdriver
Odoo deployment tool (addon)

This module ensure an up-to-date state of modules. As a developer you don't
have to worry any manual deployment steps anymore.
You have to provide a list of modules that should be installed or remove
an already installed module from the config file in order of uninstall.

## Decision matrix

| Expected status | Status      | Condition             | Action     |
|:---------------:|:-----------:| --------------------- |:----------:|
| uninstalled     | installed   |                       | uninstall  |
| uninstalled     | uninstalled |                       | do nothing |
| installed       | uninstalled |                       | install    |
| installed       | installed   |                       | do nothing |
| installed       | installed   | ver Avail != ver Inst | upgrade    |
| upgraded        | uninstalled |                       | install    |
| upgraded        | installed   |                       | upgrade    |


## Usage

```bash
    $ odoo.py screwdriver -d <database name> -f <screwdriver config>
```

## Options

--scratch
    Drop and create a database


## Config file

Yaml configuration. The file should have an entry called addons which
should be a mapping between name of modules and expected state (as above).
The module name is the internal name (like 'sale' instead of 'Sale...').

### Example

```yaml
---
addons:
    sale: installed
    hr: updated
    purchase: uninstalled
```

## Development

First, you have to build the image

```bash
    $ ./build.sh
```
It will build an image called `purple-screwdriver`. The you have to create
a data container.

```bash
    $ docker run --name purple-screwdriver-data purple-screwdriver
```

For development, (by default) the odoo.sh expect a container called `database`
too. It should be a proper postgresql database server.
You don't have to create database though - the screwdriver will do. Just make
sure the expected user (for dev superuser recommended).
For more details about user, database name, etc have a look the 
`dev/openerp-server.conf`.

```bash
    $ ./odoo.sh ...             # Odoo entrypoint
    $ ./odoo.sh screwdriver ... # Screwdriver entrypoint
    $ ./odoo.sh cli ...         # cli entrypoint
