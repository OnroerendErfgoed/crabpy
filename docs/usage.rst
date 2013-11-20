============
Using CRABpy
============

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

.. _agiv: http://www.agiv.be
