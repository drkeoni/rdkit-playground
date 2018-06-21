# rdkit Experiments

## Introduction

A code base for experimenting with [rdkit](http://www.rdkit.org/) and associated cheminformatics libraries.

## Miscellaneous

This code base uses virtualenv for its python work and as such I didn't want to use
a system install of rdkit.  Unfortunately rdkit is only available as a system-wide
install (not pip-installable).

I got around this limitation by doing the following:

```
brew install rdkit --with-python3
mkdir rdkit_wheel
cp -r /usr/local/lib/python3.6/site-packages/rdkit rdkit_wheel/
cd rdkit_wheel
```

Create a file named `setup.py` in this directory with the following contents:
```
import os
from setuptools import setup
from setuptools.dist import Distribution

DISTNAME = "rdkit"
DESCRIPTION = ""
MAINTAINER = "Jon Sorenson"
MAINTAINER_EMAIL = "jon_m_sorenson@yahoo.com"
URL = ""
LICENSE = ""
DOWNLOAD_URL = ""
VERSION = "2017.09.03"
PYTHON_VERSION = (3,6)

class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(foo):
        return True

def find_packages(root):
    paths = [root]
    for (path, directories, filenames) in os.walk(root):
        for d in directories:
            paths.append(os.path.join(path, d))
    return paths

DATA_SUFFIXES=['.so','.pbm','.pil','.pil.1','.dat','.ttf']

def find_data(root):
    paths = []
    for (path, directories, filenames) in os.walk(root):
        for f in filenames:
            if any(f.endswith(s) for s in DATA_SUFFIXES):
                paths.append((path, f))
    data = {}
    for k,v in paths:
        if k not in data:
            data[k] = []
        data[k].append(v)
    return data

setup(name=DISTNAME,
      description=DESCRIPTION,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      url=URL,
      license=LICENSE,
      download_url=DOWNLOAD_URL,
      version=VERSION,
      packages=find_packages('rdkit'),
      # Include pre-compiled .so files
      package_data=find_data('rdkit'),
      distclass=BinaryDistribution
)
```

Then create a wheel with `python3 setup.py bdist_wheel`.  I copied this wheel
to `etc/wheels` in this package and pip installed it into my virtualenv.
