0.2.0 (??-12-2013)
------------------

- Better test coverage. Ability to skip integration tests.
- Added a :class:`Gateway <crabpy.gateway.capakey.CapakeyGateway>` for the 
  Capakey webservice.
- Added caching to the Capakey Gateway using 
  `Dogpile <https://bitbucket.org/zzzeek/dogpile.cache>`_
- Added some documentation.
- Removed a dependency for resolving UsernameDigestTokens. This in term removed
  the original suds from the dependency chain.
- Due to removing those dependencies, compatibility with Python 3.2 is now 
  possible.

0.1.0 (25-10-2013)
------------------

- Initial release
- A working client for the CRAB webservice.
- A working client for the CapaKey webservice.
