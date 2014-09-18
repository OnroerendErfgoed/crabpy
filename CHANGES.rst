0.4.2 (18-09-2014)
------------------

- Fix an issue with CRAB Gateway list operations that contain no results. 
  Previously these triggered an error, now they return an empty list. (#33)
- Clean up CHANGES.rst so it works on pypi again.

0.4.1 (05-09-2014)
------------------

- Fix an issues with pickling in list_gemeente_by_provincie.
- Removed the sort parameter from list_gemeenten_by_provincie since it didn't
  work anyway.

0.4.0 (03-09-2014)
------------------

- Added a bounding box to a CRAB Straat. (#26)
- Added a bounding box to a CRAB Huisnummer. (#27)
- Added a Provincie object. (#31)

0.3.5 (02-09-2014)
------------------

- Fix hardcoded url in client.py. (#25)

0.3.4 (07-05-2014)
------------------

- Optimise lazy loading of capakey Gemeente. (#21)
- Optimise lazy loading of capakey Afdeling. (#22)
- General lazy loading optimisations.
- Some slight changes to CRAB lazy loading. (#24)

0.3.3 (02-05-2014)
------------------

- Added some debugging calls to allow an implementing application to track what
  calls are being made.

0.3.2 (07-04-2014)
------------------

- A `Gebouw` loaded through the 
  `crabpy.gateway.crab.CrabGateway.get_gebouw_by_id` was not passed a 
  `crabpy.gateway.crab.CrabGateway`. (#15)
- Always load a full `crabpy.gateway.crab.Metadata` object when returning
  from a get*_by_id method. (#13)
- Add a `wegobjecten` property to a `crabpy.gateway.crab.Straat`. (#17)
- Add a `wegsegmenten` property to a `crabpy.gateway.crab.Straat`. (#18)
- Added support for `Coveralls <https://coveralls.io>`_. (#16)

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

- Added a `Gateway <crabpy.gateway.crab.CrabGateway>` for the 
  Crab webservice.
- Added caching to the Crab Gateway using 
  `Dogpile <https://bitbucket.org/zzzeek/dogpile.cache>`_

0.2.1 (21-02-2014)
------------------

- Document how to connect to the services through a proxy.
- Fix an incomplete release.

0.2.0 (03-12-2013)
------------------

- Added a `Gateway <crabpy.gateway.capakey.CapakeyGateway>` for the 
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
