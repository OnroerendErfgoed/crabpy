===========
Development
===========

Crabpy is still in alpha development. Currently we're just happy to have gotten
a SOAP service working in python.

We try to cover as much code as we can with unit tests. You can run them using
tox_ or directly through nose:

.. code-block:: bash

    $ tox
    # No coverage
    $ nosetests 
    # Coverage
    $ nosetests --config nose_cover.cfg

If you have access to the capakey service, you can enter your credentials in 
the `nose_development.ini` file and use that as a test config.

.. code-block:: bash

    # Integration tests with nose but no coverage
    $ nosetests --tc-file nose_development.ini
    # Integration tests with nose and coverage
    $ nosetests --tc-file nose_development.ini --config nose_cover.cfg

.. _tox: http://tox.testrun.org
