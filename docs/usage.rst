============
Using CRABpy
============

Using the CRAB webservice
-------------------------

Recently, the CRAB service has become public. The need to authenticate has been
removed, making it a whole lot easier to connect. A utility function 
:func:`crabpy.client.crab_request` has been provided, similar to 
:func:`crabpy.client.capakey_request`. This allows for a slightly different way 
of calling methods on the service.


.. literalinclude:: /../examples/crab.py
   :language: python


Using the CAPAKEY webservice
----------------------------

This service does still require authentication. This requires a valid account 
from agiv_. Because the authentication also requires some extra WS-Addressing 
headers, a utility function :func:`crabpy.client.capakey_request` has been 
provided to make life easier.

.. literalinclude:: /../examples/capakey.py
   :language: python

Be careful: the CAPAKEY SOAP gateway is deprecated. We advise you the use the CAPAKEY REST gateway instead.


Using a client behind a proxy
-----------------------------

If you need to connect to CRAB or CAPAKEY through a proxy, you can do so 
by passing the proxy parameter to the :func:`crabpy.client.crab_factory` or
:func:`crabpy.client.capakey_factory`.


.. literalinclude:: /../examples/crab_proxy.py
   :language: python


Using the CRAB gateway
----------------------

To make life easier and crab more pythonic, we've also implemented a gateway
that abstracts some more of the service and provides richer objects as responses.

.. literalinclude:: /../examples/crab_gateway.py
   :language: python

The CRAB gateway supports caching through the dogpile_ caching library. Caching can
be added by passing a configuration dictionary to the :class:`CrabGateway`.

Three caching regions will be configured:

- `permanent`: For requests that can be cached for a very long time,
  eg. `list_gewesten` or `list_gemeenten`.
- `long`: For requests that can be cached for a fairly long time, 
  eg. `list_straten`.
- `short`: For requests that will only be cached for a little while, 
  eg. `get_huisnummer_by_id`.

.. literalinclude:: /../examples/crab_gateway_caching.py
   :language: python


Using the CAPAKEY gateway
-------------------------

To make life easier and capakey more pythonic, we've also implemented a gateway
that abstracts some more of the service and provides richer objects as responses.

.. literalinclude:: /../examples/capakey_gateway.py
   :language: python

The CAPAKEY gateway supports caching through the dogpile_ caching library. Caching can
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
   :language: python


See the examples folder for some more sample code.


.. warning::

   Be careful: the CAPAKEY SOAP gateway is deprecated. We advise you the use the CAPAKEY REST gateway instead.

Using the CAPAKEY REST gateway
------------------------------

To make life easier and capakey more pythonic, we've also implemented a rest gateway
that abstracts some more of the service and provides richer objects as responses.

.. literalinclude:: /../examples/capakey_restgateway.py
   :language: python

The CAPAKEY REST gateway supports caching through the dogpile_ caching library. Caching can
be added by passing a configuration dictionary to the :class:`CapakeyRestGateway`.

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

.. literalinclude:: /../examples/capakey_gateway_rest_caching.py
   :language: python


See the examples folder for some more sample code.

.. _agiv: http://www.agiv.be
.. _dogpile: https://bitbucket.org/zzzeek/dogpile.cache
