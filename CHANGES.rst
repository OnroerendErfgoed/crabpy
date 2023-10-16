1.2.6 (16-10-2023)
------------------

- Gateway terugplaatsen na serializen

1.2.5 (13-10-2023)
------------------

- Gateway niet langer cachen (#232)

1.2.4 (23-05-2023)
------------------

- Foute lijst van deelgemeenten gebruikt (#225)

1.2.3 (15-05-2023)
------------------

- Limiet van list op 1000 items (#221)

1.2.2 (09-05-2023)
------------------

- get percelen timeout (#217)

1.2.1 (04-05-2023)
------------------

- Adressenregister bugfixes

1.2.0 (04-05-2023)
------------------

- uniformiseer alles naar niscodes en check dat alle niscodes strings zijn (#208)
- errors checken en fine tunen (#209)

1.1.0 (03-05-2023)
------------------

- Lijst gemeenten statisch maken (#203)

1.0.0 (13-04-2023)
------------------

- Naar v2 van adressenregister (#185)
- File wordt niet geclosed (#133)
- black, flake8, python2 weg en pre-commit (#195)
- Uitbreidingen aan adressenregister model (#192)
- pip install van crabpy installeert ook een "tests" met alle data van crabpy (#165)

0.16.1 (29-03-2023)
-------------------

- Add user agent header to geo.api calls (#190)

0.16.0 (29-03-2023)
-------------------

- Overschakelen naar nieuwe AGIV services (#183)

0.15.0 (10-12-2021)
-------------------

- Methode list_straten kan meer data laden (#172)

0.14.0 (18-11-2021)
-------------------

- Bounding box geeft strings ipv floats (#168)

0.13.0 (14-09-2021)
-------------------

- Verwijderen python 2 support (#160)
- Vervangen suds-jurko door suds-py (#160)
- Upgraden requirements

0.12.1 (28-01-2021)
-------------------

- Adres toegevoegd aan Perceel (#147)

0.12.0 (24-06-2019)
-------------------

- Switchen naar v2 van de capakey REST-API (#120)
- Mocken van calls naar externe url's bij testen (#118)
- get_perceel_by_coordinates (#121)

0.11.0 (03-01-2019)
-------------------

- Update deelgemeenten (#110, #116)
- Fix travis tests (#112)
- Update dependencies

0.10.0 (17-07-2018)
-------------------

- Capakey service: change source base map (#95)
- Capakey service: return full geometry (#96)

0.9.0 (20-03-2018)
------------------

- Remove the deprecated CapakeyGateway (#92)


0.8.3 (07-12-2017)
------------------

- Fix some unit tests.
- Update some dependencies
- Configure pyup

0.8.2 (25-08-2017)
------------------
- Add zope.deprecation to setup.py #76
- Upgrade capakey rest service #78


0.8.1 (20-04-2017)
------------------

- Updated center and bounding box format in responses of the CapakeyRestGateway
  in accordance with the CapakeyGateway (#73).

0.8.0 (19-04-2017)
------------------

- Added a CapakeyRestGateway that uses the new Capakey REST service provided by
  Informatie Vlaanderen. (#45, #53)
- Deprecate Capakey SOAP gateway (#69)
- Fix a bug with list_huisnummers_by_perceel. (#67)
- Dropped support for Python 3.3 and added support for Python 3.6.

0.7.0 (25-01-2016)
------------------

- Add official support for python 3.5
- Implement list_huisnummers_by_perceel. (#56)
- Implement get_postadres_by_huisnummer and get_postadres_by_subadres. (#57)
- A a property Perceel.postadressen to get the postadressen for a certain
  Perceel. (#58)
- Implement a Deelgemeente object and list_deelgemeenten,
  list_deelgemeenten_by_gemeente and get_deelgemeente_by_id. (#63)

0.6.0 (01-06-2015)
------------------

- Implement operations dealing with Adrespositie. (#37) [TalissaJoly]
- Improve the coverage. (#39) [TalissaJoly]
- Fix a bug with objects that have an empty bounding box. (#46) [TalissaJoly]
- Better handling of unexisting objects. (#49) [TalissaJoly]
- Switch tests to py.test. (#19) [TalissaJoly]

0.5.0 (03-03-2015)
------------------

- Implement operations dealing with Subadres. This deals with things like
  postboxes in appartment complexes. (#34) (#40) [TalissaJoly]
- Drop support for python 3.2 (#36)
- Fix a bug with crab.list_aardsubadressen. (#38)

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
