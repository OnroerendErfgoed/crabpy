#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

packages = [
    "crabpy",
]

requires = ["suds-py3>=1.4.4.1", "dogpile.cache", "requests"]

setup(
    name="crabpy",
    version="1.2.1",
    description="Interact with geographical webservices by Informatie Vlaanderen.",
    long_description=open("README.rst").read() + "\n\n" + open("CHANGES.rst").read(),
    author="Onroerend Erfgoed",
    author_email="ict@onroerenderfgoed.be",
    url="http://github.com/onroerenderfgoed/crabpy",
    packages=find_packages(exclude=["tests*"]),
    package_data={"": ["LICENSE"]},
    package_dir={"crabpy": "crabpy"},
    include_package_data=True,
    install_requires=requires,
    entry_points="""\
      [paste.app_factory]
      main = crabpy:main""",
    license="MIT",
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
