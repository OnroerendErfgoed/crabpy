#!/usr/bin/env python

import os
import sys

import crabpy

from setuptools import setup, find_packages

packages = [
    'crabpy',
]

requires = [
    'suds-jurko>=0.6.0',
    'dogpile.cache',
    'six',
    'requests'
]

setup(
    name='crabpy',
    version='0.9.0',
    description='Interact with geographical webservices by Informatie Vlaanderen.',
    long_description=open('README.rst').read() + '\n\n' +
                     open('CHANGES.rst').read(),
    author='Onroerend Erfgoed',
    author_email='ict@onroerenderfgoed.be',
    url='http://github.com/onroerenderfgoed/crabpy',
    packages=find_packages(),
    package_data={'': ['LICENSE']},
    package_dir={'crabpy': 'crabpy'},
    include_package_data=True,
    install_requires=requires,
    entry_points="""\
      [paste.app_factory]
      main = crabpy:main""",
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='nose.collector'
)
