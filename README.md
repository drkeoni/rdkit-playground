# rdkit Experiments

## Introduction

A code base for experimenting with [rdkit](http://www.rdkit.org/) and associated cheminformatics libraries.

## Miscellaneous

This code base uses virtualenv for its python work and as such I didn't want to use
a system install of rdkit.  Unfortunately rdkit is only available as a system-wide
install (not pip-installable).

I got around this limitation by doing the following:

```
brew tap rdkit/rdkit
brew install rdkit --with-python3
mkdir rdkit_wheel
cp -r /usr/local/lib/python3.6/site-packages/rdkit rdkit_wheel/
cd rdkit_wheel
```

Copy [setup.py](bin/setup.py) to `rdkit_wheel`.

Then create a wheel with `python3 setup.py bdist_wheel`.  I copied this wheel
to `etc/wheels` in this package and pip installed it into my virtualenv.
