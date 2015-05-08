===========
Development
===========

Crabpy is still in development, but the general API is stable and we are already 
using it in production. Generally we're also just happy to have gotten a SOAP 
service working in python.

We try to cover as much code as we can with unit tests. You can run them using
tox_ or directly through py.test.

.. code-block:: bash

    $ tox
    # No coverage
    $ py.test
    # Coverage
    $ py.test --cov crabpy --cov-report term-missing tests/

If you have access to the capakey service, you can enter your credentials in 
the `pytest_dist.ini` file and use that as a test config. It's actually best to
copy this file and edit the copy instead of the original.

.. code-block:: ini

   [pytest]
   addopts = --crab-integration --capakey-integration --capakey-user=<username> --capakey-password=<password>

.. code-block:: bash

    # Integration tests but no coverage
    $ py.test -c pytest_<user>.ini
    # Integration tests with coverage
    $ py.test -c pytest_<user>.ini --cov crabpy --cov-report term-missing tests/
    # Running just the CRAB integration tests without using a config file
    $ py.test --crab-integration --cov crabpy --cov-report term-missing tests/

.. _tox: http://tox.testrun.org
