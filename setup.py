"""
API - EO Data Cube.

Python Client Library for Earth Observation Data Cubes.
This abstraction uses STAC.py library provided by BDC Project.

=======================================
begin                : 2021-05-01
git sha              : $Format:%H$
copyright            : (C) 2020 by none
email                : none@inpe.br
=======================================

This program is free software.
You can redistribute it and/or modify it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
"""

import os

from setuptools import find_packages, setup

docs_require = [
    'Sphinx>=2.2',
    'sphinx_rtd_theme',
    'sphinx-copybutton'
]

tests_require = [
    'pytest>=5.2',
    'pytest-cov>=2.8',
    'pytest-pep8>=1.0',
    'pydocstyle>=4.0',
    'isort>4.3',
    'check-manifest>=0.40'
]

extras_require = {
    'docs': docs_require,
    'tests': tests_require
}

extras_require['all'] = [req for _, reqs in extras_require.items() for req in reqs]

setup_requires = [
    'pytest-runner>=5.2'
]

install_requires = [
    'numpy>=1.19',
    'matplotlib>=3.3.3',
    'pandas>=1.1',
    'requests>=2',
    'xarray>=0.18.2',
    'stac.py>=0.9',
    'pyproj',
    'dask',
    'rasterio'    
]

packages = find_packages()

g = {}
with open(os.path.join('eocube', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='eocube',
    version=version,
    description=__doc__,
    long_description="Python Client Library for Earth Observation Data Cubes",
    long_description_content_type = 'text/x-rst',
    keywords=['Earth Observation Data Cube', 'GIS', 'QGIS'],
    license='MIT',
    author='Geo Programming Group 4 Team',
    author_email='abner.anjos@inpe.br',
    url='https://github.com/AbnerErnaniADSFatec/in-prog-geo',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={},
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 1 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: GIS',
    ]
)
