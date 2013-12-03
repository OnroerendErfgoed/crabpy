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
