CRABpy
======

This library provides access to the CRAB and CAPAKEY webservices operated by 
the AGIV. Because connecting to these SOAP services from python can be somewhat 
complicated, this library makes it easier.

.. image:: https://travis-ci.org/OnroerendErfgoed/crabpy.png?branch=master
        :target: https://travis-ci.org/OnroerendErfgoed/crabpy

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

.. _agiv: http://www.agiv.be
.. _tox: http://tox.testrun.org
