CRABpy
======

This library provides access to the CRAB and CAPAKEY webservices operated by 
the AGIV. Because connecting to these SOAP services from python can be somewhat 
complicated, this library makes it easier.

.. image:: https://travis-ci.org/OnroerendErfgoed/crabpy.png?branch=master
        :target: https://travis-ci.org/OnroerendErfgoed/crabpy
.. image:: https://badge.fury.io/py/crabpy.png
        :target: http://badge.fury.io/py/crabpy
.. image:: https://coveralls.io/repos/OnroerendErfgoed/crabpy/badge.png?branch=master 
        :target: https://coveralls.io/r/OnroerendErfgoed/crabpy?branch=master 

Using the CRAB webservice
-------------------------

Recently, the CRAB service has become public. The need to authenticate has been
removed, making it a whole lot easier to connect.

.. code-block:: python

    from crabpy.client import crab_factory

    crab = crab_factory()

    res = crab.service.ListGemeentenByGewestId(1)

    print res

Using the CAPAKEY webservice
----------------------------

This service does still require authentication. This requires a valid account 
from agiv_. Because the authentication also requires some extra WS-Addressing 
headers, a utility function has been provided to make life easier.

.. code-block:: python

    from crabpy.client import capakey_factory, capakey_request

    capakey = capakey_factory(
        user='USER',
        password='PASSWORD'
    )

    res = capakey_request(capakey, 'ListAdmGemeenten', 1)

    print res

Using the CAPAKEY gateway
-------------------------

To make life easier and capakey more pythonic, we've also implemented a gateway
that abstracts some more of the service and provides richer objects as responses.

.. code-block:: python

    from crabpy.client import capakey_factory
    from crabpy.gateway.capakey import CapakeyGateway

    capakey = capakey_factory(
        user='USER',
        password='PASSWORD'
    )

    g = CapakeyGateway(capakey)

    res = g.list_gemeenten()

    print res

See the examples folder for some more sample code.

Development
-----------

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

.. _agiv: http://www.agiv.be
.. _tox: http://tox.testrun.org
