"""
setup.py script for creating Mac OS X rdkit wheels

To create an rdkit wheel:
    1. Install rdkit at the system-level using brew
    2. mkdir work_dir && cp setup.py work_dir/ && cd work_dir
    3. cp /usr/local/lib/python3.7/site-packages/rdkit .
    4. python3 setup.py bdist_wheel

Wheel will be built to work_dir/dist
"""
import sys
import os
import subprocess
import glob

from setuptools import setup
from setuptools.dist import Distribution

DISTNAME = "rdkit"
DESCRIPTION = ""
MAINTAINER = "Jon Sorenson"
MAINTAINER_EMAIL = "jon_m_sorenson@yahoo.com"
URL = ""
LICENSE = ""
DOWNLOAD_URL = ""
# Change me for different versions
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

DATA_SUFFIXES=['.so','.pbm','.pil','.pil.1','.dat','.ttf','.dylib']

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

def exe(cmd):
    try:
        print('Executing %s'%cmd, file=sys.stderr)
        out = subprocess.check_output( cmd, shell=True )
        str_out = out.decode('utf-8')
        return str_out, 0
    except subprocess.CalledProcessError:
        print('%s failed'%cmd,file=sys.stderr)
        return '%s failed'%cmd, 1
    except:
        print('%s unknown error'%cmd,file=sys.stderr)
        return '%s unknown error', 1

def copy_dylibs(src_lib_dir,tgt_lib_dir):
    exe( 'mkdir -p %s' % tgt_lib_dir )
    exe( 'cp %s/libRD* %s/' % ( src_lib_dir, tgt_lib_dir ))

def reset_ids(lib_dir):
    lib_path = os.path.join(lib_dir,'*.dylib')
    dylib_files = glob.glob(lib_path)
    print('Found %d dylibs to update at %s'%(len(dylib_files),lib_path),file=sys.stderr)
    for dylib in dylib_files:
        lib_name = os.path.basename(dylib)
        exe('chmod oug+w %s'%dylib)
        exe('install_name_tool -id "@rpath/%s" %s'%(lib_name,dylib))

def change_lookups(lib,depth):
    out, ret_code = exe('otool -L %s | grep libRD'%lib)
    if ret_code>0:
        return None
    dylibs = [l.strip().split()[0] for l in out.split('\n') if len(l)>0]
    exe('chmod oug+w %s'%lib)
    up_dirs = '../'*depth
    for dylib in dylibs:
        exe('install_name_tool -change %s @loader_path/%slib/%s %s'%(dylib,up_dirs,os.path.basename(dylib),lib))

def change_all_lookups(root):
    paths = []
    for (path, directories, filenames) in os.walk(root):
        for f in filenames:
            if f.endswith('.so'):
                depth = path.count('/')
                change_lookups(os.path.join(path,f),depth)

copy_dylibs('/usr/local/lib', 'rdkit/lib')
reset_ids('rdkit/lib')
change_all_lookups('rdkit')

setup(name=DISTNAME,
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
