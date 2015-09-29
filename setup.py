# -*- coding: utf-8  -*-
"""Installer script for pywikibase."""
#
# (C) Pywikibot team, 2015
#
# Distributed under the terms of the MIT license.
#

import sys

from setuptools import find_packages, setup

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
version = '0.1a'
github_url = 'https://github.com/wikimedia/pywikibot-wikibase'

setup(
    name=name,
    version=version,
    description='Python package to handle Wikibase DataModel',
    long_description=open('README.rst').read(),
    maintainer='The Pywikibot team',
    maintainer_email='pywikibot@lists.wikimedia.org',
    license='MIT License',
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
