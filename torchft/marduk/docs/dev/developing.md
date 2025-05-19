# Developing

If you rewrote the rust code, you need to reinstall the python package.

```bash
pip install -e .
```

## Style Guide

There should be no constants in the python code. All constants should be in the `constants.py` file.

Make sure that all the code is well-documented and easy to understand.

Reuse as much code as possible, unless this introduces unnecessary complexity.