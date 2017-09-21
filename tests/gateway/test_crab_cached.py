# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest

from crabpy.client import (
    crab_factory
)

from crabpy.gateway.crab import (
    CrabGateway, Gewest, Provincie,
    Gemeente, Deelgemeente, Straat,
    Huisnummer, Postkanton,
    Wegobject, Wegsegment,
    Terreinobject, Perceel,
    Gebouw, Subadres,
    Adrespositie
)

@pytest.mark.skipif(
    not pytest.config.getoption('--crab-integration'),
    reason='No CRAB Integration tests required'
)
class TestCrabCachedGateway:

    def setup_method(self, method):
        self.crab_client = crab_factory()
        self.crab = CrabGateway(
            self.crab_client,
            cache_config={
                'permanent.backend': 'dogpile.cache.memory',
                'permanent.expiration_time': 86400,
                'long.backend': 'dogpile.cache.memory',
                'long.expiration_time': 3600,
                'short.backend': 'dogpile.cache.memory',
                'short.expiration_time': 600,
            }
        )

    def teardown_method(self, method):
        self.crab_client = None
        self.crab = None

    def test_cache_is_configured(self):
        from dogpile.cache.backends.memory import MemoryBackend
        assert isinstance(
            self.crab.caches['permanent'].backend,
            MemoryBackend
        )
        assert self.crab.caches['permanent'].is_configured

    def test_list_gewesten(self):
        res = self.crab.list_gewesten()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListGewesten#1') == res

    def test_list_gewesten_different_sort(self):
        res = self.crab.list_gewesten(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListGewesten#2') == res
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListGewesten#1') == NO_VALUE

    def test_list_provincies(self):
        res = self.crab.list_provincies(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListProvinciesByGewestId#2') == res
        assert res[0].gewest.id == 2

    def test_get_provincie_by_id(self):
        res = self.crab.get_provincie_by_id(10000)
        assert isinstance(res, Provincie)
        assert self.crab.caches['permanent'].get('GetProvincieByProvincieNiscode#10000') == res

    def test_list_gemeenten_default_is_Vlaanderen(self):
        res = self.crab.list_gemeenten()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListGemeentenByGewestId#2#1') == res
        assert res[0].gewest.id == 2

    def test_list_gemeenten_gewest_1(self):
        gewest = Gewest(1)
        r = self.crab.list_gemeenten(gewest)
        assert isinstance(r, list)
        assert self.crab.caches['permanent'].get('ListGemeentenByGewestId#1#1') == r
        assert r[0].gewest.id == 1

    def test_list_gemeenten_different_sort(self):
        res = self.crab.list_gemeenten(2, 1)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListGemeentenByGewestId#2#1') == res
        gewest = Gewest(2)
        r = self.crab.list_gemeenten(gewest, 2)
        assert isinstance(r, list)
        assert self.crab.caches['permanent'].get('ListGemeentenByGewestId#2#2') == r
        assert not res == r

    def test_list_gemeenten_by_provincie(self):
        res = self.crab.list_gemeenten_by_provincie(10000)
        provincie = self.crab.get_provincie_by_id(10000)
        assert isinstance(res, list)
        assert self.crab.caches['long'].get('ListGemeentenByProvincieId#10000') == res
        provincie = self.crab.get_provincie_by_id(10000)
        res = self.crab.list_gemeenten_by_provincie(provincie)
        assert isinstance(res, list)
        assert self.crab.caches['long'].get('ListGemeentenByProvincieId#10000') == res

    def test_get_gemeente_by_id(self):
        res = self.crab.get_gemeente_by_id(1)
        assert isinstance(res, Gemeente)
        assert self.crab.caches['long'].get('GetGemeenteByGemeenteId#1') == res

    def test_get_gemeente_by_niscode(self):
        res = self.crab.get_gemeente_by_niscode(11001)
        assert isinstance(res, Gemeente)
        assert self.crab.caches['long'].get('GetGemeenteByNISGemeenteCode#11001') == res

    def test_list_deelgemeenten_by_gemeente(self):
        res = self.crab.list_deelgemeenten_by_gemeente(45062)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListDeelgemeentenByGemeenteId#45062') == res
        gemeente = self.crab.get_gemeente_by_niscode(45062)
        res = self.crab.list_deelgemeenten_by_gemeente(gemeente)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListDeelgemeentenByGemeenteId#45062') == res

    def test_get_deelgemeente_by_id(self):
        res = self.crab.get_deelgemeente_by_id('45062A')
        assert isinstance(res, Deelgemeente)
        assert self.crab.caches['permanent'].get('GetDeelgemeenteByDeelgemeenteId#45062A') == res

    def test_list_talen(self):
        res = self.crab.list_talen()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListTalen#1') == res

    def test_list_talen_different_sort(self):
        res = self.crab.list_talen(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListTalen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListTalen#1') == NO_VALUE

    def test_list_bewerkingen(self):
        res = self.crab.list_bewerkingen()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListBewerkingen#1') == res

    def test_list_bewerkingen_different_sort(self):
        res = self.crab.list_bewerkingen(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListBewerkingen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListBewerkingen#1') == NO_VALUE

    def test_list_organisaties(self):
        res = self.crab.list_organisaties()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListOrganisaties#1') == res

    def test_list_organisaties_different_sort(self):
        res = self.crab.list_organisaties(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListOrganisaties#2') == res
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListOrganisaties#1') == NO_VALUE

    def test_list_aardadressen(self):
        res = self.crab.list_aardadressen()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListAardAdressen#1') == res

    def test_list_aardadressen_different_sort(self):
        res = self.crab.list_aardadressen(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListAardAdressen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListAardAdressen#1') == NO_VALUE

    def test_list_aardgebouwen(self):
        res = self.crab.list_aardgebouwen()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListAardGebouwen#1') == res

    def test_list_aardgebouwen_different_sort(self):
        res = self.crab.list_aardgebouwen(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListAardGebouwen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListAardGebouwen#1') == NO_VALUE

    def test_list_aardwegobjecten(self):
        res = self.crab.list_aardwegobjecten()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListAardWegobjecten#1') == res

    def test_list_aardwegobjecten_different_sort(self):
        res = self.crab.list_aardwegobjecten(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListAardWegobjecten#2') == res
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListAardWegobjecten#1') == NO_VALUE

    def test_list_aardterreinobjecten(self):
        res = self.crab.list_aardterreinobjecten()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListAardTerreinobjecten#1') == res

    def test_list_aardterreinobjecten_different_sort(self):
        res = self.crab.list_aardterreinobjecten(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListAardTerreinobjecten#2') == res
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListAardTerreinobjecten#1') == NO_VALUE

    def test_list_statushuisnummers(self):
        res = self.crab.list_statushuisnummers()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListStatusHuisnummers#1') == res

    def test_list_statushuisnummers_different_sort(self):
        res = self.crab.list_statushuisnummers(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListStatusHuisnummers#2') == res
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListStatusHuisnummers#1') == NO_VALUE

    def test_list_statussubadressen(self):
        res = self.crab.list_statussubadressen()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListStatusSubadressen#1') == res

    def test_list_statussubadressen_different_sort(self):
        res = self.crab.list_statussubadressen(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListStatusSubadressen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListStatusSubadressen#1') == NO_VALUE

    def test_list_statusstraatnamen(self):
        res = self.crab.list_statusstraatnamen()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListStatusStraatnamen#1') == res

    def test_list_statusstraatnamen_different_sort(self):
        res = self.crab.list_statusstraatnamen(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListStatusStraatnamen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListStatusStraatnamen#1') == NO_VALUE

    def test_list_statuswegsegmenten(self):
        res = self.crab.list_statuswegsegmenten()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListStatusWegsegmenten#1') == res

    def test_list_statuswegsegmenten_different_sort(self):
        res = self.crab.list_statuswegsegmenten(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListStatusWegsegmenten#2') == res

        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListStatusWegsegmenten#1') == NO_VALUE

    def test_list_geometriemethodewegsegmenten(self):
        res = self.crab.list_geometriemethodewegsegmenten()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListGeometriemethodeWegsegmenten#1') == res

    def test_list_geometriemethodewegsegmenten_different_sort(self):
        res = self.crab.list_geometriemethodewegsegmenten(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListGeometriemethodeWegsegmenten#2') == res
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListGeometriemethodeWegsegmenten#1') == NO_VALUE

    def test_list_statusgebouwen(self):
        res = self.crab.list_statusgebouwen()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListStatusGebouwen#1') == res

    def test_list_statusgebouwen_different_sort(self):
        res = self.crab.list_statusgebouwen(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListStatusGebouwen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListStatusGebouwen#1') == NO_VALUE

    def test_list_geometriemethodegebouwen(self):
        res = self.crab.list_geometriemethodegebouwen()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListGeometriemethodeGebouwen#1') == res

    def test_list_geometriemethodegebouwen_different_sort(self):
        res = self.crab.list_geometriemethodegebouwen(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListGeometriemethodeGebouwen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListGeometriemethodeGebouwen#1') == NO_VALUE

    def test_list_herkomstadrespositie(self):
        res = self.crab.list_herkomstadresposities()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListHerkomstAdresposities#1') == res

    def test_list_herkomstadrespositie_different_sort(self):
        res = self.crab.list_herkomstadresposities(2)
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListHerkomstAdresposities#2') == res
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['permanent'].get('ListHerkomstAdresposities#1') == NO_VALUE

    def test_list_straten(self):
        res = self.crab.list_straten(1)
        assert isinstance(res, list)
        assert self.crab.caches['long'].get('ListStraatnamenWithStatusByGemeenteId#11') == res
        gem = self.crab.get_gemeente_by_id(2)
        r = self.crab.list_straten(gem)
        assert isinstance(r, list)
        assert self.crab.caches['long'].get('ListStraatnamenWithStatusByGemeenteId#21') == r

    def test_list_straten_different_sort(self):
        res = self.crab.list_straten(1, 2)
        assert isinstance(res, list)
        assert self.crab.caches['long'].get('ListStraatnamenWithStatusByGemeenteId#12') == res
        gem = self.crab.get_gemeente_by_id(2)
        r = self.crab.list_straten(gem, 2)
        assert isinstance(r, list)
        assert self.crab.caches['long'].get('ListStraatnamenWithStatusByGemeenteId#22') == r
        from dogpile.cache.api import NO_VALUE
        assert self.crab.caches['long'].get('ListStraatnamenWithStatusByGemeenteId#11') == NO_VALUE

    def test_get_straat_by_id(self):
        res = self.crab.get_straat_by_id(1)
        assert isinstance(res, Straat)
        assert self.crab.caches['long'].get('GetStraatnaamWithStatusByStraatnaamId#1') == res

    def test_list_huisnummers_by_straat(self):
        res = self.crab.list_huisnummers_by_straat(1)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListHuisnummersWithStatusByStraatnaamId#11') == res
        straat = self.crab.get_straat_by_id(2)
        r = self.crab.list_huisnummers_by_straat(straat)
        assert isinstance(r, list)
        assert self.crab.caches['short'].get('ListHuisnummersWithStatusByStraatnaamId#21') == r

    def test_list_huisnummers_by_perceel(self):
        res = self.crab.list_huisnummers_by_perceel('13040C1747/00G002')
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListHuisnummersWithStatusByIdentificatorPerceel#13040C1747/00G0021') == res
        perceel = self.crab.get_perceel_by_id('13040C1747/00H002')
        r = self.crab.list_huisnummers_by_perceel(perceel)
        assert isinstance(r, list)
        assert self.crab.caches['short'].get('ListHuisnummersWithStatusByIdentificatorPerceel#13040C1747/00H0021') == r

    def test_list_huisnummers_by_straat_different_sort(self):
        res = self.crab.list_huisnummers_by_straat(1, 2)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListHuisnummersWithStatusByStraatnaamId#12') == res
        straat = self.crab.get_straat_by_id(2)
        r = self.crab.list_huisnummers_by_straat(straat, 2)
        assert isinstance(r, list)
        assert self.crab.caches['short'].get('ListHuisnummersWithStatusByStraatnaamId#22') == r

    def test_get_huisnummer_by_id(self):
        res = self.crab.get_huisnummer_by_id(1)
        assert isinstance(res, Huisnummer)
        assert self.crab.caches['short'].get('GetHuisnummerWithStatusByHuisnummerId#1') == res

    def test_get_huisnummer_by_nummer_and_straat(self):
        res = self.crab.get_huisnummer_by_nummer_and_straat(1, 1)
        assert isinstance(res, Huisnummer)
        assert self.crab.caches['short'].get('GetHuisnummerWithStatusByHuisnummer#11') == res
        straat = self.crab.get_straat_by_id(1)
        res = self.crab.get_huisnummer_by_nummer_and_straat(1, straat)
        assert isinstance(res, Huisnummer)
        assert self.crab.caches['short'].get("GetHuisnummerWithStatusByHuisnummer#11") == res

    def test_list_postkantons_by_gemeente(self):
        res = self.crab.list_postkantons_by_gemeente(1)
        assert isinstance(res, list)
        assert self.crab.caches['long'].get('ListPostkantonsByGemeenteId#1') == res
        gemeente = self.crab.get_gemeente_by_id(2)
        r = self.crab.list_postkantons_by_gemeente(gemeente)
        assert isinstance(r, list)
        assert self.crab.caches['long'].get('ListPostkantonsByGemeenteId#2') == r

    def test_get_postkanton_by_huisnummer(self):
        res = self.crab.get_postkanton_by_huisnummer(1)
        assert isinstance(res, Postkanton)
        assert self.crab.caches['short'].get('GetPostkantonByHuisnummerId#1') == res
        huisnummer = self.crab.get_huisnummer_by_id(1)
        r = self.crab.get_postkanton_by_huisnummer(huisnummer)
        assert isinstance(r, Postkanton)
        assert self.crab.caches['short'].get('GetPostkantonByHuisnummerId#1') == r

    def test_list_wegobjecten_by_straat(self):
        res = self.crab.list_wegobjecten_by_straat(1)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListWegobjectenByStraatnaamId#1') == res
        straat = self.crab.get_straat_by_id(2)
        res = self.crab.list_wegobjecten_by_straat(straat)
        assert self.crab.caches['short'].get('ListWegobjectenByStraatnaamId#2') == res

    def test_get_wegobject_by_id(self):
        res = self.crab.get_wegobject_by_id("53839893")
        assert isinstance(res, Wegobject)
        assert self.crab.caches['short'].get('GetWegobjectByIdentificatorWegobject#53839893') == res

    def test_list_wegsegmenten_by_straat(self):
        res = self.crab.list_wegsegmenten_by_straat(1)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListWegsegmentenByStraatnaamId#1') == res
        straat = self.crab.get_straat_by_id(2)
        r = self.crab.list_wegsegmenten_by_straat(straat)
        assert self.crab.caches['short'].get('ListWegsegmentenByStraatnaamId#2') == r

    def test_get_wegsegment_by_id(self):
        res = self.crab.get_wegsegment_by_id("108724")
        assert isinstance(res, Wegsegment)
        assert self.crab.caches['short'].get('GetWegsegmentByIdentificatorWegsegment#108724') == res

    def test_list_terreinobjecten_by_huisnummer(self):
        res = self.crab.list_terreinobjecten_by_huisnummer(1)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListTerreinobjectenByHuisnummerId#1') == res
        huisnummer = self.crab.get_huisnummer_by_id(1)
        res = self.crab.list_terreinobjecten_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListTerreinobjectenByHuisnummerId#1') == res

    def test_get_terreinobject_by_id(self):
        res = self.crab.get_terreinobject_by_id("13040_C_1747_G_002_00")
        assert isinstance(res, Terreinobject)
        assert self.crab.caches['short'].get('GetTerreinobjectByIdentificatorTerreinobject#13040_C_1747_G_002_00') == res

    def test_list_percelen_by_huisnummer(self):
        res = self.crab.list_percelen_by_huisnummer(1)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListPercelenByHuisnummerId#1') == res
        huisnummer = self.crab.get_huisnummer_by_id(1)
        res = self.crab.list_percelen_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListPercelenByHuisnummerId#1') == res

    def test_get_perceel_by_id(self):
        res = self.crab.get_perceel_by_id("13040C1747/00G002")
        assert isinstance(res, Perceel)
        assert self.crab.caches['short'].get('GetPerceelByIdentificatorPerceel#13040C1747/00G002') == res

    def test_list_gebouwen_by_huisnummer(self):
        res = self.crab.list_gebouwen_by_huisnummer(1)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListGebouwenByHuisnummerId#1') == res
        huisnummer = self.crab.get_huisnummer_by_id(1)
        res = self.crab.list_gebouwen_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListGebouwenByHuisnummerId#1') == res

    def test_get_gebouw_by_id(self):
        res = self.crab.get_gebouw_by_id("1538575")
        assert isinstance(res, Gebouw)
        assert self.crab.caches['short'].get('GetGebouwByIdentificatorGebouw#1538575') == res

    def test_list_subadressen_by_huisnummer(self):
        res = self.crab.list_subadressen_by_huisnummer(129462)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListSubadressenWithStatusByHuisnummerId#129462') == res
        huisnummer = self.crab.get_huisnummer_by_id(129462)
        res = self.crab.list_subadressen_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListSubadressenWithStatusByHuisnummerId#129462') == res

    def test_get_subadres_by_id(self):
        res = self.crab.get_subadres_by_id(1120934)
        assert isinstance(res, Subadres)
        assert self.crab.caches['short'].get('GetSubadresWithStatusBySubadresId#1120934') == res

    def test_list_adresposities_by_huisnummer(self):
        res = self.crab.list_adresposities_by_huisnummer(1)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListAdrespositiesByHuisnummerId#1') == res

    def test_list_adresposities_by_nummer_and_straat(self):
        res = self.crab.list_adresposities_by_nummer_and_straat(1, 1)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListAdrespositiesByHuisnummer#11') == res

    def test_list_adresposities_by_subadres(self):
        res = self.crab.list_adresposities_by_subadres(1120936)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListAdrespositiesBySubadresId#1120936') == res

    def test_list_adresposities_by_subadres_and_huisnummer(self):
        res = self.crab.list_adresposities_by_subadres_and_huisnummer('A', 129462)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListAdrespositiesBySubadres#A129462') == res
        huisnummer = self.crab.get_huisnummer_by_id(129462)
        res = self.crab.list_adresposities_by_subadres_and_huisnummer('A', huisnummer)
        assert isinstance(res, list)
        assert self.crab.caches['short'].get('ListAdrespositiesBySubadres#A129462') == res

    def test_get_adrespositie_by_id(self):
        res = self.crab.get_adrespositie_by_id(4428005)
        assert isinstance(res, Adrespositie)
        assert str(self.crab.caches['short'].get('GetAdrespositieByAdrespositieId#4428005')) == str(res)

    def test_get_postadres_by_huisnummer(self):
        res = self.crab.get_postadres_by_huisnummer(1)
        assert res == 'Steenweg op Oosthoven 51, 2300 Turnhout'
        assert str(self.crab.caches['short'].get('GetPostadresByHuisnummerId#1')) == str(res)

    def test_get_postadres_by_subadres(self):
        res = self.crab.get_postadres_by_subadres(1120936)
        assert res == 'Antoon van Brabantstraat 7 bus B, 2630 Aartselaar'
        assert str(self.crab.caches['short'].get('GetPostadresBySubadresId#1120936')) == str(res)
