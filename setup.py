#!/usr/bin/env python

import os
import sys

import crabpy

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'crabpy',
]

requires = [
    'suds-jurko',
    'suds-passworddigest'
]

setup(
    name='crabpy',
    version='0.1.0a1',
    description='Interact with AGIV webservices.',
    long_description=open('README.rst').read() + '\n\n' +
                     open('CHANGES.rst').read(),
    author='Onroerend Erfgoed',
    author_email='ict@onroerenderfgoed.be',
    url='http://github.com/onroerenderfgoed/crabpy',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'crabpy': 'crabpy'},
    include_package_data=True,
    install_requires=requires,
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='nose.collector'
)
