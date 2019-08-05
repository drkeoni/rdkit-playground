import sys
import os
import subprocess
import glob

from setuptools import setup
from setuptools.dist import Distribution

SYS_PKG_HOME = "/usr/local/lib/python3.7/site-packages/rdkit"
DISTNAME = "rdkit"
DESCRIPTION = ""
MAINTAINER = "Jon Sorenson"
MAINTAINER_EMAIL = "jon_m_sorenson@yahoo.com"
URL = ""
LICENSE = ""
DOWNLOAD_URL = ""
VERSION = "2019.03.08"
PYTHON_VERSION = (3, 6)
DATA_SUFFIXES = ['.so', '.pbm', '.pil', '.pil.1', '.dat', '.ttf', '.dylib']


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


def find_data(root):
    paths = []
    for (path, directories, filenames) in os.walk(root):
        for f in filenames:
            if any(f.endswith(s) for s in DATA_SUFFIXES):
                paths.append((path, f))
    data = {}
    for k, v in paths:
        if k not in data:
            data[k] = []
        data[k].append(v)
    return data


def _exe(cmd):
    try:
        print(f'Executing {cmd}', file=sys.stderr)
        out = subprocess.check_output(cmd, shell=True)
        str_out = out.decode('utf-8')
        return str_out, 0
    except subprocess.CalledProcessError:
        print(f'{cmd} failed', file=sys.stderr)
        return f'{cmd} failed', 1
    except:
        print(f'{cmd} unknown error', file=sys.stderr)
        return f'{cmd} unknown error', 1


def copy_dylibs(src_lib_dir, tgt_lib_dir):
    _exe(f'mkdir -p {tgt_lib_dir}')
    _exe(f'cp {src_lib_dir}/libRD* {tgt_lib_dir}/')


def reset_ids(lib_dir):
    lib_path = os.path.join(lib_dir, '*.dylib')
    dylib_files = glob.glob(lib_path)
    print(f'Found {len(dylib_files)} dylibs to update at {lib_path}', file=sys.stderr)
    for dylib in dylib_files:
        lib_name = os.path.basename(dylib)
        _exe(f'chmod oug+w {dylib}')
        _exe(f'install_name_tool -id "@rpath/{lib_name}" {dylib}')


def change_lookups(lib, depth):
    out, ret_code = _exe(f'otool -L {lib} | grep libRD')
    if ret_code > 0:
        return None
    dylibs = [l.strip().split()[0] for l in out.split('\n') if len(l)>0]
    _exe(f'chmod oug+w {lib}')
    up_dirs = '../' * depth
    for dylib in dylibs:
        _exe(f'install_name_tool -change {dylib} @loader_path/{up_dirs}lib/{os.path.basename(dylib)} {lib}')


def change_all_lookups(root):
    for (path, directories, filenames) in os.walk(root):
        for f in filenames:
            if f.endswith('.so'):
                depth = path.count('/')
                change_lookups(os.path.join(path, f), depth)


_exe('rm -rf rdkit')
_exe(f'cp -r {SYS_PKG_HOME} .')
copy_dylibs('/usr/local/lib', 'rdkit/lib')
reset_ids('rdkit/lib')
change_all_lookups('rdkit')

setup(
    name=DISTNAME,
    description=DESCRIPTION,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    url=URL,
    license=LICENSE,
    download_url=DOWNLOAD_URL,
    version=VERSION,
    packages=find_packages('rdkit'),
    # Include pre-compiled .so files, etc...
    package_data=find_data('rdkit'),
    distclass=BinaryDistribution
)
