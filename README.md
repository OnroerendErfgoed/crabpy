# CRABpy

This library provides access to the CRAB and CAPAKEY webservices operated by
the AGIV. Because connecting to these SOAP services from python can be somewhat
complicated, this library makes it easier.

[![docs](https://readthedocs.org/projects/crabpy/badge/?version=latest)](https://readthedocs.org/projects/crabpy/?badge=latest)
[![pypi](https://badge.fury.io/py/crabpy.png)](http://badge.fury.io/py/crabpy)
[![CI](https://github.com/OnroerendErfgoed/crabpy/actions/workflows/backend.yaml/badge.svg)](https://github.com/OnroerendErfgoed/crabpy/actions/workflows/backend.yaml)
[![Coverage](https://coveralls.io/repos/OnroerendErfgoed/crabpy/badge.png?branch=master)](https://coveralls.io/r/OnroerendErfgoed/crabpy?branch=master)


## Build wheel or sdist

```sh
pip install hatch
hatch build
hatch build -t wheel
hatch build -t sdist
```


## Work with pip-compile / pip-sync

full docs: https://pip-tools.readthedocs.io/en/latest/

To start, first install pip-tools: 
```sh
pip install pip-tools
```

### uv (optional)

You can also use `uv` and for the remainder of the readme replace `pip`, `pip-compile` or
`pip-sync` by `uv pip`, `uv pip compile` and `uv pip sync`.

`uv` is a very fast replacement for pip-toools. It's optional, but can save a lot of time.
```sh
pip install uv
```

### Install requirements: pip-sync

Note, `pip-sync` also uninstalls everything from the virtualenv which does not belong 
there according to the requirements file. This includes the project itself. You will
have to install `crabpy` again after `pip-sync`.
Since the requirements file of pip-sync is still a normal requirements file you can also
use `pip install -r` to install all libraries defined in it. This will not cleanup your
virtualenv and uninstall other libraries.

The compiled requirements files are made in a 3.11 environment.
```sh
pip-sync requirements-dev.txt
pip install -e .
```
`requirements-dev.txt` contains all libraries uncluding those for testing and development.

`requirements.txt` contains only the necessary libraries for running the library.

### Update requirements: pip-compile

```sh
echo -e "\nStarting"
PIP_COMPILE_ARGS="-q --strip-extras --no-header --resolver=backtracking --no-emit-options pyproject.toml"
pip-compile $PIP_COMPILE_ARGS -o requirements.txt;
echo "requirements.txt done"
pip-compile $PIP_COMPILE_ARGS --extra dev -o requirements-dev.txt;
echo "requirements-dev.txt done"
echo "Finished"
```
