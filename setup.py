# -*- coding: utf-8  -*-
"""Installer script for pywikibase."""
#
# (C) Pywikibot team, 2015
#
# Distributed under the terms of the MIT license.
#

import os
import sys

from setuptools import find_packages, setup

about_path = os.path.join(os.path.dirname(__file__), "pywikibase/about.py")
exec(compile(open(about_path).read(), about_path, "exec"))


PYTHON_VERSION = sys.version_info[:3]
PY2 = (PYTHON_VERSION[0] == 2)
PY26 = (PYTHON_VERSION < (2, 7))

versions_required_message = """
Pywikibase not available on:
%s

Pywikibase is only supported under Python 2.6.5+, 2.7.2+ or 3.3+
"""


def python_is_supported():
    """Check that Python is supported."""
    # Any change to this must be copied to pwb.py
    return (PYTHON_VERSION >= (3, 3, 0) or
            (PY2 and PYTHON_VERSION >= (2, 7, 2)) or
            (PY26 and PYTHON_VERSION >= (2, 6, 5)))


if not python_is_supported():
    raise RuntimeError(versions_required_message % sys.version)


dependencies = []
dependency_links = []


name = 'pywikibase'
version = '0.0.3'

setup(
    name=__name__,  # noqa
    version=__version__,  # noqa
    description=__description__,  # noqa
    maintainer=__maintainer__,  # noqa
    maintainer_email=__maintainer_email__,  # noqa
    license=__license__,  # noqa
    long_description=open('README.rst').read(),
    install_requires=dependencies,
    dependency_links=dependency_links,
    packages=find_packages(),
    url='https://www.mediawiki.org/wiki/Pywikibot',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
    use_2to3=True,
)
