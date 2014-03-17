0.3.1 (17-03-2014)
------------------

- Fixed a bug with lazy loading a Perceel's capatype or cashkey. (#8)
- Removes duplicates from a list of gemeentes as returned by CRAB. (#10)
- Removed loading a Gemeente with an afdeling to speed up certain queries. (#7)
- Removed a few unneeded requests in the capakey gateway when working with 
  Gemeente.id or Afdeling.id.
- Fixed printing of objects through the __str__ method on python 2.7. (#9)
- Adapted examples for python 3 print. (#11)

0.3.0 (12-03-2014)
------------------

- Added a :class:`Gateway <crabpy.gateway.crab.CrabGateway>` for the 
  Crab webservice.
- Added caching to the Crab Gateway using 
  `Dogpile <https://bitbucket.org/zzzeek/dogpile.cache>`_

0.2.1 (21-02-2014)
------------------

- Document how to connect to the services through a proxy.
- Fix an incomplete release.

0.2.0 (03-12-2013)
------------------

- Added a :class:`Gateway <crabpy.gateway.capakey.CapakeyGateway>` for the 
  Capakey webservice.
- Added caching to the Capakey Gateway using 
  `Dogpile <https://bitbucket.org/zzzeek/dogpile.cache>`_
- Better test coverage. Ability to skip integration tests.
- Added some documentation.
- Removed a dependency for resolving UsernameDigestTokens. This in term removed
  the original suds from the dependency chain.
- Due to removing those dependencies, compatibility with Python 3.2 and 3.3 is 
  now present.

0.1.0 (25-10-2013)
------------------

- Initial release
- A working client for the `CRAB webservice <http://www.agiv.be/gis/diensten/?catid=156>`_.
- A working client for the `CapaKey webservice <http://www.agiv.be/gis/diensten/?catid=138>`_.
