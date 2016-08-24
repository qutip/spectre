#!/usr/bin/env python
"""Spectre: Sepectral wavefunction solver

Spectre is a package designed to solve for the eigenvalues
and corresponding wavefunctions of a N-dimesional (N <= 3) 
potential using spectral methods.
"""

DOCLINES = __doc__.split('\n')

CLASSIFIERS = """\
Development Status :: 4 - Beta
Intended Audience :: Science/Research
License :: OSI Approved :: BSD License
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Scientific/Engineering
Operating System :: MacOS
Operating System :: POSIX
Operating System :: Unix
Operating System :: Microsoft :: Windows
"""

# import statements
import os
import sys

# The following is required to get unit tests up and running.
# If the user doesn't have, then that's OK, we'll just skip unit tests.
try:
    import setuptools
    TEST_SUITE = 'nose.collector'
    TESTS_REQUIRE = ['nose']
    EXTRA_KWARGS = {
        'test_suite': TEST_SUITE,
        'tests_require': TESTS_REQUIRE
    }
except:
    EXTRA_KWARGS = {}

try:
    import numpy as np
    from numpy.distutils.core import setup
except ImportError:
    np = None
    try:
        from setuptools import setup
    except ImportError:
        from distutils.core import setup


# all information about QuTiP goes here
MAJOR = 0
MINOR = 1
MICRO = 0
ISRELEASED = False
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)
REQUIRES = ['numpy (>=1.8)', 'scipy (>=0.15)']
INSTALL_REQUIRES = ['numpy>=1.8', 'scipy>=0.15']
PACKAGES = ['spectre']
PACKAGE_DATA = {}
# If we're missing numpy, exclude import directories until we can
# figure them out properly.
INCLUDE_DIRS = []
EXT_MODULES = []
NAME = "spectre"
AUTHOR = "Paul D. Nation"
AUTHOR_EMAIL = "nonhermitian@gmail.com"
LICENSE = "BSD"
DESCRIPTION = DOCLINES[0]
LONG_DESCRIPTION = "\n".join(DOCLINES[2:])
KEYWORDS = "quantum physics wave function"
URL = "http://qutip.org"
CLASSIFIERS = [_f for _f in CLASSIFIERS.split('\n') if _f]
PLATFORMS = ["Linux", "Mac OSX", "Unix", "Windows"]


def git_short_hash():
    try:
        return "+" + os.popen('git log -1 --format="%h"').read().strip()
    except:
        return ""

FULLVERSION = VERSION
if not ISRELEASED:
    FULLVERSION += '.dev'+str(MICRO)+git_short_hash()

if np is None:
    EXTRA_KWARGS['version'] = FULLVERSION

def write_version_py(filename='spectre/version.py'):
    cnt = """\
# THIS FILE IS GENERATED FROM SPECTRE SETUP.PY
short_version = '%(version)s'
version = '%(fullversion)s'
release = %(isrelease)s
"""
    a = open(filename, 'w')
    try:
        a.write(cnt % {'version': VERSION, 'fullversion':
                FULLVERSION, 'isrelease': str(ISRELEASED)})
    finally:
        a.close()

local_path = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(local_path)
sys.path.insert(0, local_path)
sys.path.insert(0, os.path.join(local_path, 'spectre'))  # to retrive _version

# always rewrite _version
if os.path.exists('spectre/version.py'):
    os.remove('spectre/version.py')

write_version_py()


# using numpy distutils to simplify install of data directory for testing
def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration

    config = Configuration(None, parent_package, top_path)
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)

    config.add_subpackage('spectre')
    config.get_version('spectre/version.py')  # sets config.version

    return config


# Setup commands go here
setup(
    name = NAME,
    configuration = configuration,
    packages = PACKAGES,
    include_dirs = INCLUDE_DIRS,
    ext_modules = EXT_MODULES,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    license = LICENSE,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    keywords = KEYWORDS,
    url = URL,
    classifiers = CLASSIFIERS,
    platforms = PLATFORMS,
    requires = REQUIRES,
    package_data = PACKAGE_DATA,
    zip_safe = False,
    install_requires=INSTALL_REQUIRES,
    **EXTRA_KWARGS
)
