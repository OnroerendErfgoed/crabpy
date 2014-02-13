============
Using CRABpy
============

Using the CRAB webservice
-------------------------

Recently, the CRAB service has become public. The need to authenticate has been
removed, making it a whole lot easier to connect.

.. literalinclude:: /../examples/crab_gateway.py

.. code-block:: python

    from crabpy.client import crab_factory

    crab = crab_factory()

    res = crab.service.ListGemeentenByGewestId(1)
    print res

    res = crab.service.ListPostkantonsByGemeenteId(71)
    print res

    res = crab.service.ListStraatnamenWithStatusByGemeenteId(71)
    print res 

    res = crab.service.ListHuisnummersWithStatusByStraatnaamId(18618)
    print res

    res = crab.service.GetStraatnaamWithStatusByStraatnaamId(18618)
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

Using a client behing a proxy
-----------------------------

If you need to connect to CRAB or CAPAKEY through a proxy, you can do so 
by passing the proxy parameter to the :func:`crabpy.client.crab_factory` or
:func:`crabpy.client.capakey_factory`.


.. literalinclude:: /../examples/crab_proxy.py


Using the CAPAKEY gateway
-------------------------

To make life easier and capakey more pythonic, we've also implemented a gateway
that abstracts some more of the service and provides richer objects as responses.

.. literalinclude:: /../examples/capakey_gateway.py

The capakey supports caching through the dogpile_ caching library. Caching can
be added by passing a configuration dictionary to the :class:`CapakeyGateway`.

Three caching regions will be configured:

- `permanent`: For requests that can be cached for a very long time,
  eg. `list_gemeenten`.
- `long`: For requests that can be cached for a fairly long time, 
  eg. `list_secties_by_afdeling`.
- `short`: For requests that will only be cached for a little while, 
  eg. `get_perceel_by_capakey`.

Please bear in mind that in this case short can probably be fairly long. We 
suspect that the database underlying the capakey service is not updated that
regularly, so a short caching duration could easily be one hour or even a day.

.. literalinclude:: /../examples/capakey_gateway_caching.py




See the examples folder for some more sample code.

.. _agiv: http://www.agiv.be
.. _dogpile: https://bitbucket.org/zzzeek/dogpile.cache
