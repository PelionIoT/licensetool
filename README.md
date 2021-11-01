# LicenseTool

LicenseTool is a Python program that has two primary functions:

1. Format the Yocto build produced `license.manifest` formatted file to CSV-formatted file.
    - CSV aka Comma-Separated-Values -files are commonly accepted by many applications and libraries as a data format.
    - This way you can import the package license information for example to Excel for further analysis
1. Take two Yocto build `license.manifest` files and create a CSV-formatted file that shows the changes between the two builds.
    - A typical Yocto build will have 1000 or more packages.
    - It is quite difficult to spot the changes between two builds without some help.

## Installation


## Usage

### Generate CSV-formatted license file

`python licensetool.py csv <input manifest file> <output CSV-file>`

### Generate license changes file

`python licensetool.py changes <previous manifest file> <current manifest file> <output CSV-file>`


## Tests

Tests and test material are located in [tests](tests)-folder.
You can them from the root folder:

```
pytest --cov=licensetool --cov-report term-missing tests/
```

## Contributions

All contributions must be done with compliance to Apache 2.0 license.
All contributions must pass:
- Code review, so submit a pull request (PR).
- Run `pylint licensetool.py` and make sure the score does not get worse (9.82 now).
- Include necessary test case updates, so that coverage does not decrease - provide evidence in the PR.
- Include required documentation updates.
