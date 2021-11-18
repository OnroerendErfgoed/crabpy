import pytest
from unittest.mock import Mock

from crabpy.gateway.crab import (
    Gewest, Provincie,
    Gemeente, Deelgemeente, Straat,
    Huisnummer, Postkanton,
    Wegobject, Wegsegment,
    Terreinobject, Perceel,
    Gebouw, Subadres,
    Adrespositie
)


class TestCrabCachedGateway:

    @pytest.fixture(scope='function')
    def crab_gateway(self, crab_gateway, crab_client_mock):
        crab_gateway.__init__(
            crab_client_mock,
            cache_config={
                'permanent.backend': 'dogpile.cache.memory',
                'permanent.expiration_time': 86400,
                'long.backend': 'dogpile.cache.memory',
                'long.expiration_time': 3600,
                'short.backend': 'dogpile.cache.memory',
                'short.expiration_time': 600,
            }
        )
        return crab_gateway

    def test_cache_is_configured(self, crab_gateway):
        from dogpile.cache.backends.memory import MemoryBackend
        assert isinstance(
            crab_gateway.caches['permanent'].backend,
            MemoryBackend
        )
        assert crab_gateway.caches['permanent'].is_configured

    def test_list_gewesten(self, crab_gateway, crab_service):
        crab_service.ListGewesten.return_value = Mock(
            GewestItem=[
                Mock(GewestId=1, TaalCodeGewestNaam='NL', GewestNaam='Vlaams')
            ]
        )
        res = crab_gateway.list_gewesten()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListGewesten#1') == res

    def test_list_gewesten_different_sort(self, crab_gateway, crab_service):
        crab_service.ListGewesten.return_value = Mock(
            GewestItem=[
                Mock(GewestId=1, TaalCodeGewestNaam='NL', GewestNaam='Vlaams')
            ]
        )
        res = crab_gateway.list_gewesten(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListGewesten#2') == res
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListGewesten#1') == NO_VALUE

    def test_list_provincies(self, crab_gateway):
        res = crab_gateway.list_provincies(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListProvinciesByGewestId#2') == res
        assert res[0].gewest.id == 2

    def test_get_provincie_by_id(self, crab_gateway):
        res = crab_gateway.get_provincie_by_id(10000)
        assert isinstance(res, Provincie)
        assert crab_gateway.caches['permanent'].get('GetProvincieByProvincieNiscode#10000') == res

    def test_list_gemeenten_default_is_vlaanderen(self, crab_gateway,
                                                  crab_service):
        crab_service.GetGewestByGewestIdAndTaalCode.return_value = Mock(
            GewestId=2,
        )
        crab_service.ListGemeentenByGewestId.return_value = Mock(
            GemeenteItem=[
                Mock(GemeenteId=1, NISGemeenteCode=10000,
                     TaalCode='NL', TaalCodeGemeenteNaam='NL')
            ]
        )
        res = crab_gateway.list_gemeenten()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListGemeentenByGewestId#2#1') == res
        assert res[0].gewest.id == 2

    def test_list_gemeenten_gewest_1(self, crab_gateway, crab_service):
        crab_service.GetGewestByGewestIdAndTaalCode.return_value = Mock(
            GewestId=1,
        )
        crab_service.ListGemeentenByGewestId.return_value = Mock(
            GemeenteItem=[
                Mock(GemeenteId=1, NISGemeenteCode=10000,
                     TaalCode='NL', TaalCodeGemeenteNaam='NL')
            ]
        )
        gewest = Gewest(1)
        r = crab_gateway.list_gemeenten(gewest)
        assert isinstance(r, list)
        assert crab_gateway.caches['permanent'].get('ListGemeentenByGewestId#1#1') == r
        assert r[0].gewest.id == 1

    def test_list_gemeenten_different_sort(self, crab_gateway, crab_service):
        crab_service.GetGewestByGewestIdAndTaalCode.return_value = Mock(
            GewestId=1,
        )
        crab_service.ListGemeentenByGewestId.return_value = Mock(
            GemeenteItem=[
                Mock(GemeenteId=1, NISGemeenteCode=10000,
                     TaalCode='NL', TaalCodeGemeenteNaam='NL')
            ]
        )
        res = crab_gateway.list_gemeenten(2, 1)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListGemeentenByGewestId#2#1') == res
        gewest = Gewest(2)
        r = crab_gateway.list_gemeenten(gewest, 2)
        assert isinstance(r, list)
        assert crab_gateway.caches['permanent'].get('ListGemeentenByGewestId#2#2') == r
        assert not res == r

    def test_list_gemeenten_by_provincie(self, crab_gateway, crab_service):
        crab_service.GetGewestByGewestIdAndTaalCode.return_value = Mock(
            GewestId=2
        )
        crab_service.ListGemeentenByGewestId.return_value = Mock(
            GemeenteItem=[
                Mock(GemeenteId=1, NISGemeenteCode=10000,
                     TaalCode='NL', TaalCodeGemeenteNaam='NL')
            ]
        )
        res = crab_gateway.list_gemeenten_by_provincie(10000)
        assert isinstance(res, list)
        assert crab_gateway.caches['long'].get('ListGemeentenByProvincieId#10000') == res
        provincie = Provincie(10000, 'Antwerpen', Gewest(2))
        res = crab_gateway.list_gemeenten_by_provincie(provincie)
        assert isinstance(res, list)
        assert crab_gateway.caches['long'].get('ListGemeentenByProvincieId#10000') == res

    def test_get_gemeente_by_id(self, crab_gateway, crab_service):
        crab_service.GetGemeenteByGemeenteId.return_value = Mock(
            GemeenteId=1, GewestId=1, BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.get_gemeente_by_id(1)
        assert isinstance(res, Gemeente)
        assert crab_gateway.caches['long'].get('GetGemeenteByGemeenteId#1') == res

    def test_get_gemeente_by_niscode(self, crab_gateway, crab_service):
        crab_service.GetGemeenteByNISGemeenteCode.return_value = Mock(
            GemeenteId=1, GewestId=1, NisGemeenteCode=11001, BeginBewerking=1,
            BeginOrganisatie=1
        )
        res = crab_gateway.get_gemeente_by_niscode(11001)
        assert isinstance(res, Gemeente)
        assert crab_gateway.caches['long'].get('GetGemeenteByNISGemeenteCode#11001') == res

    def test_list_deelgemeenten_by_gemeente(self, crab_gateway, crab_service):
        crab_service.GetGemeenteByNISGemeenteCode.return_value = Mock(
            GemeenteId=1, GewestId=1, BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.list_deelgemeenten_by_gemeente(45062)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListDeelgemeentenByGemeenteId#45062') == res
        gemeente = Gemeente(1, None, 45062, None)
        res = crab_gateway.list_deelgemeenten_by_gemeente(gemeente)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListDeelgemeentenByGemeenteId#45062') == res

    def test_get_deelgemeente_by_id(self, crab_gateway):
        res = crab_gateway.get_deelgemeente_by_id('45062A')
        assert isinstance(res, Deelgemeente)
        assert crab_gateway.caches['permanent'].get('GetDeelgemeenteByDeelgemeenteId#45062A') == res

    def test_list_talen(self, crab_gateway, crab_service):
        crab_service.ListTalen.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_talen()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListTalen#1') == res

    def test_list_talen_different_sort(self, crab_gateway, crab_service):
        crab_service.ListTalen.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_talen(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListTalen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListTalen#1') == NO_VALUE

    def test_list_bewerkingen(self, crab_gateway, crab_service):
        res = crab_gateway.list_bewerkingen()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListBewerkingen#1') == res

    def test_list_bewerkingen_different_sort(self, crab_gateway, crab_service):
        res = crab_gateway.list_bewerkingen(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListBewerkingen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListBewerkingen#1') == NO_VALUE

    def test_list_organisaties(self, crab_gateway, crab_service):
        res = crab_gateway.list_organisaties()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListOrganisaties#1') == res

    def test_list_organisaties_different_sort(self, crab_gateway, crab_service):
        res = crab_gateway.list_organisaties(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListOrganisaties#2') == res
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListOrganisaties#1') == NO_VALUE

    def test_list_aardadressen(self, crab_gateway, crab_service):
        crab_service.ListAardAdressen.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_aardadressen()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListAardAdressen#1') == res

    def test_list_aardadressen_different_sort(self, crab_gateway, crab_service):
        crab_service.ListAardAdressen.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_aardadressen(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListAardAdressen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListAardAdressen#1') == NO_VALUE

    def test_list_aardgebouwen(self, crab_gateway, crab_service):
        crab_service.ListAardGebouwen.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_aardgebouwen()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListAardGebouwen#1') == res

    def test_list_aardgebouwen_different_sort(self, crab_gateway,
                                              crab_service):
        crab_service.ListAardGebouwen.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_aardgebouwen(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListAardGebouwen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListAardGebouwen#1') == NO_VALUE

    def test_list_aardwegobjecten(self, crab_gateway, crab_service):
        crab_service.ListAardWegobjecten.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_aardwegobjecten()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListAardWegobjecten#1') == res

    def test_list_aardwegobjecten_different_sort(self, crab_gateway,
                                                 crab_service):
        crab_service.ListAardWegobjecten.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_aardwegobjecten(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListAardWegobjecten#2') == res
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListAardWegobjecten#1') == NO_VALUE

    def test_list_aardterreinobjecten(self, crab_gateway, crab_service):
        crab_service.ListAardTerreinobjecten.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_aardterreinobjecten()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListAardTerreinobjecten#1') == res

    def test_list_aardterreinobjecten_different_sort(self, crab_gateway,
                                                     crab_service):
        crab_service.ListAardTerreinobjecten.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_aardterreinobjecten(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListAardTerreinobjecten#2') == res
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListAardTerreinobjecten#1') == NO_VALUE

    def test_list_statushuisnummers(self, crab_gateway, crab_service):
        crab_service.ListStatusHuisnummers.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_statushuisnummers()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListStatusHuisnummers#1') == res

    def test_list_statushuisnummers_different_sort(self, crab_gateway,
                                                   crab_service):
        crab_service.ListStatusHuisnummers.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_statushuisnummers(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListStatusHuisnummers#2') == res
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListStatusHuisnummers#1') == NO_VALUE

    def test_list_statussubadressen(self, crab_gateway, crab_service):
        crab_service.ListStatusSubadressen.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_statussubadressen()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListStatusSubadressen#1') == res

    def test_list_statussubadressen_different_sort(self, crab_gateway,
                                                   crab_service):
        crab_service.ListStatusSubadressen.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_statussubadressen(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListStatusSubadressen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListStatusSubadressen#1') == NO_VALUE

    def test_list_statusstraatnamen(self, crab_gateway, crab_service):
        crab_service.ListStatusStraatnamen.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_statusstraatnamen()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListStatusStraatnamen#1') == res

    def test_list_statusstraatnamen_different_sort(self, crab_gateway,
                                                   crab_service):
        crab_service.ListStatusStraatnamen.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_statusstraatnamen(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListStatusStraatnamen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListStatusStraatnamen#1') == NO_VALUE

    def test_list_statuswegsegmenten(self, crab_gateway, crab_service):
        crab_service.ListStatusWegsegmenten.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_statuswegsegmenten()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListStatusWegsegmenten#1') == res

    def test_list_statuswegsegmenten_different_sort(self, crab_gateway,
                                                    crab_service):
        crab_service.ListStatusWegsegmenten.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_statuswegsegmenten(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListStatusWegsegmenten#2') == res

        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListStatusWegsegmenten#1') == NO_VALUE

    def test_list_geometriemethodewegsegmenten(self, crab_gateway,
                                               crab_service):
        crab_service.ListGeometriemethodeWegsegmenten.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_geometriemethodewegsegmenten()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListGeometriemethodeWegsegmenten#1') == res

    def test_list_geometriemethodewegsegmenten_different_sort(
            self, crab_gateway, crab_service):
        crab_service.ListGeometriemethodeWegsegmenten.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_geometriemethodewegsegmenten(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListGeometriemethodeWegsegmenten#2') == res
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListGeometriemethodeWegsegmenten#1') == NO_VALUE

    def test_list_statusgebouwen(self, crab_gateway, crab_service):
        crab_service.ListStatusGebouwen.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_statusgebouwen()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListStatusGebouwen#1') == res

    def test_list_statusgebouwen_different_sort(self, crab_gateway,
                                                crab_service):
        crab_service.ListStatusGebouwen.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_statusgebouwen(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListStatusGebouwen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListStatusGebouwen#1') == NO_VALUE

    def test_list_geometriemethodegebouwen(self, crab_gateway, crab_service):
        crab_service.ListGeometriemethodeGebouwen.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_geometriemethodegebouwen()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListGeometriemethodeGebouwen#1') == res

    def test_list_geometriemethodegebouwen_different_sort(self, crab_gateway,
                                                          crab_service):
        crab_service.ListGeometriemethodeGebouwen.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_geometriemethodegebouwen(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListGeometriemethodeGebouwen#2') == res
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListGeometriemethodeGebouwen#1') == NO_VALUE

    def test_list_herkomstadrespositie(self, crab_gateway, crab_service):
        crab_service.ListHerkomstAdresposities.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_herkomstadresposities()
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListHerkomstAdresposities#1') == res

    def test_list_herkomstadrespositie_different_sort(self, crab_gateway,
                                                      crab_service):
        crab_service.ListHerkomstAdresposities.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_herkomstadresposities(2)
        assert isinstance(res, list)
        assert crab_gateway.caches['permanent'].get('ListHerkomstAdresposities#2') == res
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['permanent'].get('ListHerkomstAdresposities#1') == NO_VALUE

    def test_list_straten(self, crab_gateway, crab_service):
        crab_service.ListStraatnamenWithStatusByGemeenteId.return_value = Mock(
            StraatnaamWithStatusItem=[]
        )
        res = crab_gateway.list_straten(1)
        assert isinstance(res, list)
        assert crab_gateway.caches['long'].get('ListStraatnamenWithStatusByGemeenteId#11') == res
        gem = Gemeente(2, None, None, None)
        r = crab_gateway.list_straten(gem)
        assert isinstance(r, list)
        assert crab_gateway.caches['long'].get('ListStraatnamenWithStatusByGemeenteId#21') == r

    def test_list_straten_different_sort(self, crab_gateway, crab_service):
        crab_service.ListStraatnamenWithStatusByGemeenteId.return_value = Mock(
            StraatnaamWithStatusItem=[]
        )
        res = crab_gateway.list_straten(1, 2)
        assert isinstance(res, list)
        assert crab_gateway.caches['long'].get('ListStraatnamenWithStatusByGemeenteId#12') == res
        gem = Gemeente(2, None, None, None)
        r = crab_gateway.list_straten(gem, 2)
        assert isinstance(r, list)
        assert crab_gateway.caches['long'].get('ListStraatnamenWithStatusByGemeenteId#22') == r
        from dogpile.cache.api import NO_VALUE
        assert crab_gateway.caches['long'].get('ListStraatnamenWithStatusByGemeenteId#11') == NO_VALUE

    def test_get_straat_by_id(self, crab_gateway, crab_service):
        crab_service.GetStraatnaamWithStatusByStraatnaamId.return_value = Mock(
            StraatnaamId=1, BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.get_straat_by_id(1)
        assert isinstance(res, Straat)
        assert crab_gateway.caches['long'].get('GetStraatnaamWithStatusByStraatnaamId#1') == res

    def test_list_huisnummers_by_straat(self, crab_gateway, crab_service):
        crab_service.ListHuisnummersWithStatusByStraatnaamId.return_value = (
            Mock(HuisnummerWithStatusItem=[Mock(HuisnummerId=1)])
        )
        res = crab_gateway.list_huisnummers_by_straat(1)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListHuisnummersWithStatusByStraatnaamId#11') == res
        straat = Straat(2, None, None, None)
        r = crab_gateway.list_huisnummers_by_straat(straat)
        assert isinstance(r, list)
        assert crab_gateway.caches['short'].get('ListHuisnummersWithStatusByStraatnaamId#21') == r

    def test_list_huisnummers_by_perceel(self, crab_gateway, crab_service):
        crab_service.ListHuisnummersWithStatusByIdentificatorPerceel\
            .return_value = Mock(
                HuisnummerWithStatusItem=[Mock(HuisnummerId=1)]
            )
        crab_service.GetHuisnummerWithStatusByHuisnummerId.return_value = (
            Mock(HuisnummerId=1, BeginBewerking=1, BeginOrganisatie=1)
        )
        res = crab_gateway.list_huisnummers_by_perceel('13040C1747/00G002')
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListHuisnummersWithStatusByIdentificatorPerceel#13040C1747/00G0021') == res
        perceel = Perceel('13040C1747/00H002')
        r = crab_gateway.list_huisnummers_by_perceel(perceel)
        assert isinstance(r, list)
        assert crab_gateway.caches['short'].get('ListHuisnummersWithStatusByIdentificatorPerceel#13040C1747/00H0021') == r

    def test_list_huisnummers_by_straat_different_sort(self, crab_gateway,
                                                       crab_service):
        crab_service.ListHuisnummersWithStatusByStraatnaamId.return_value = (
            Mock(HuisnummerWithStatusItem=[Mock(HuisnummerId=1)])
        )
        res = crab_gateway.list_huisnummers_by_straat(1, 2)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListHuisnummersWithStatusByStraatnaamId#12') == res
        straat = Straat(2, None, None, None)
        r = crab_gateway.list_huisnummers_by_straat(straat, 2)
        assert isinstance(r, list)
        assert crab_gateway.caches['short'].get('ListHuisnummersWithStatusByStraatnaamId#22') == r

    def test_get_huisnummer_by_id(self, crab_gateway, crab_service):
        crab_service.GetHuisnummerWithStatusByHuisnummerId.return_value = Mock(
            HuisnummerId=1, BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.get_huisnummer_by_id(1)
        assert isinstance(res, Huisnummer)
        assert crab_gateway.caches['short'].get('GetHuisnummerWithStatusByHuisnummerId#1') == res

    def test_get_huisnummer_by_nummer_and_straat(self, crab_gateway,
                                                 crab_service):
        crab_service.GetHuisnummerWithStatusByHuisnummer.return_value = Mock(
            HuisnummerId=1, BeginBewerking=1, BeginOrganisatie=1,
            Huisnummer='1'
        )
        crab_service.GetStraatnaamWithStatusByStraatnaamId.return_value = Mock(
            StraatnaamId=1, BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.get_huisnummer_by_nummer_and_straat(1, 1)
        assert isinstance(res, Huisnummer)
        assert crab_gateway.caches['short'].get('GetHuisnummerWithStatusByHuisnummer#11') == res
        straat = Straat(1, None, None, None)
        res = crab_gateway.get_huisnummer_by_nummer_and_straat(1, straat)
        assert isinstance(res, Huisnummer)
        assert crab_gateway.caches['short'].get("GetHuisnummerWithStatusByHuisnummer#11") == res

    def test_list_postkantons_by_gemeente(self, crab_gateway, crab_service):
        crab_service.ListPostkantonsByGemeenteId.return_value = Mock(
            PostkantonItem=[Mock(PostkantonCode=1)]
        )
        res = crab_gateway.list_postkantons_by_gemeente(1)
        assert isinstance(res, list)
        assert crab_gateway.caches['long'].get('ListPostkantonsByGemeenteId#1') == res
        gemeente = Gemeente(2, None, None, None)
        r = crab_gateway.list_postkantons_by_gemeente(gemeente)
        assert isinstance(r, list)
        assert crab_gateway.caches['long'].get('ListPostkantonsByGemeenteId#2') == r

    def test_get_postkanton_by_huisnummer(self, crab_gateway, crab_service):
        crab_service.GetPostkantonByHuisnummerId.return_value = Mock(
            PostkantonCode=1
        )
        res = crab_gateway.get_postkanton_by_huisnummer(1)
        assert isinstance(res, Postkanton)
        assert crab_gateway.caches['short'].get('GetPostkantonByHuisnummerId#1') == res
        huisnummer = Huisnummer(1, None, None, None)
        r = crab_gateway.get_postkanton_by_huisnummer(huisnummer)
        assert isinstance(r, Postkanton)
        assert crab_gateway.caches['short'].get('GetPostkantonByHuisnummerId#1') == r

    def test_list_wegobjecten_by_straat(self, crab_gateway, crab_service):
        crab_service.ListWegobjectenByStraatnaamId.return_value = Mock(
            WegobjectItem=[Mock(IdentificatorWegobject=1,
                                AardWegobject=1)]
        )
        res = crab_gateway.list_wegobjecten_by_straat(1)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListWegobjectenByStraatnaamId#1') == res
        straat = Straat(2, None, None, None)
        res = crab_gateway.list_wegobjecten_by_straat(straat)
        assert crab_gateway.caches['short'].get('ListWegobjectenByStraatnaamId#2') == res

    def test_get_wegobject_by_id(self, crab_gateway, crab_service):
        crab_service.GetWegobjectByIdentificatorWegobject.return_value = Mock(
            IdentificatorWegobject='53839893', BeginBewerking=1,
            BeginOrganisatie=1
        )
        res = crab_gateway.get_wegobject_by_id("53839893")
        assert isinstance(res, Wegobject)
        assert crab_gateway.caches['short'].get('GetWegobjectByIdentificatorWegobject#53839893') == res

    def test_list_wegsegmenten_by_straat(self, crab_gateway, crab_service):
        crab_service.ListWegsegmentenByStraatnaamId.return_value = Mock(
            WegsegmentItem=[Mock()]
        )
        res = crab_gateway.list_wegsegmenten_by_straat(1)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListWegsegmentenByStraatnaamId#1') == res
        straat = Straat(2, None, None, None)
        r = crab_gateway.list_wegsegmenten_by_straat(straat)
        assert crab_gateway.caches['short'].get('ListWegsegmentenByStraatnaamId#2') == r

    def test_get_wegsegment_by_id(self, crab_gateway, crab_service):
        crab_service.GetWegsegmentByIdentificatorWegsegment.return_value = (
            Mock(IdentificatorWegsegment='108724', BeginBewerking=1,
                 BeginOrganisatie=1)
        )
        res = crab_gateway.get_wegsegment_by_id("108724")
        assert isinstance(res, Wegsegment)
        assert crab_gateway.caches['short'].get('GetWegsegmentByIdentificatorWegsegment#108724') == res

    def test_list_terreinobjecten_by_huisnummer(self, crab_gateway,
                                                crab_service):
        crab_service.ListTerreinobjectenByHuisnummerId.return_value = Mock(
            TerreinobjectItem=[Mock()]
        )
        res = crab_gateway.list_terreinobjecten_by_huisnummer(1)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListTerreinobjectenByHuisnummerId#1') == res
        huisnummer = Huisnummer(1, None, None, None)
        res = crab_gateway.list_terreinobjecten_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListTerreinobjectenByHuisnummerId#1') == res

    def test_get_terreinobject_by_id(self, crab_gateway, crab_service):
        crab_service.GetTerreinobjectByIdentificatorTerreinobject\
            .return_value = Mock(
                IdentificatorTerreinobject='13040_C_1747_G_002_00',
                BeginBewerking=1, BeginOrganisatie=1
            )
        res = crab_gateway.get_terreinobject_by_id("13040_C_1747_G_002_00")
        assert isinstance(res, Terreinobject)
        assert crab_gateway.caches['short'].get('GetTerreinobjectByIdentificatorTerreinobject#13040_C_1747_G_002_00') == res

    def test_list_percelen_by_huisnummer(self, crab_gateway, crab_service):
        crab_service.ListPercelenByHuisnummerId.return_value = Mock(
            PerceelItem=[Mock()]
        )
        res = crab_gateway.list_percelen_by_huisnummer(1)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListPercelenByHuisnummerId#1') == res
        huisnummer = Huisnummer(1, None, None, None)
        res = crab_gateway.list_percelen_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListPercelenByHuisnummerId#1') == res

    def test_get_perceel_by_id(self, crab_gateway, crab_service):
        crab_service.GetPerceelByIdentificatorPerceel.return_value = Mock(
            IdentificatorPerceel='13040C1747/00G002',
            BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.get_perceel_by_id("13040C1747/00G002")
        assert isinstance(res, Perceel)
        assert crab_gateway.caches['short'].get('GetPerceelByIdentificatorPerceel#13040C1747/00G002') == res

    def test_list_gebouwen_by_huisnummer(self, crab_gateway, crab_service):
        crab_service.ListGebouwenByHuisnummerId.return_value = Mock(
            GebouwItem=[Mock(IdentificatorGebouw=1)]
        )
        res = crab_gateway.list_gebouwen_by_huisnummer(1)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListGebouwenByHuisnummerId#1') == res
        huisnummer = Huisnummer(1, None, None, None)
        res = crab_gateway.list_gebouwen_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListGebouwenByHuisnummerId#1') == res

    def test_get_gebouw_by_id(self, crab_gateway, crab_service):
        crab_service.GetGebouwByIdentificatorGebouw.return_value = Mock(
            IdentificatorGebouw=1538575, BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.get_gebouw_by_id("1538575")
        assert isinstance(res, Gebouw)
        assert crab_gateway.caches['short'].get('GetGebouwByIdentificatorGebouw#1538575') == res

    def test_list_subadressen_by_huisnummer(self, crab_gateway, crab_service):
        crab_service.ListSubadressenWithStatusByHuisnummerId.return_value = (
            Mock(SubadresWithStatusItem=[Mock(SubadresId=1)])
        )
        res = crab_gateway.list_subadressen_by_huisnummer(129462)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListSubadressenWithStatusByHuisnummerId#129462') == res
        huisnummer = Huisnummer(129462, None, None, None)
        res = crab_gateway.list_subadressen_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListSubadressenWithStatusByHuisnummerId#129462') == res

    def test_get_subadres_by_id(self, crab_gateway, crab_service):
        crab_service.GetSubadresWithStatusBySubadresId.return_value = Mock(
            SubadresId=1120936, BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.get_subadres_by_id(1120934)
        assert isinstance(res, Subadres)
        assert crab_gateway.caches['short'].get('GetSubadresWithStatusBySubadresId#1120934') == res

    def test_list_adresposities_by_huisnummer(self, crab_gateway, crab_service):
        crab_service.ListAdrespositiesByHuisnummerId.return_value = Mock(
            AdrespositieItem=[Mock()]
        )
        res = crab_gateway.list_adresposities_by_huisnummer(1)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListAdrespositiesByHuisnummerId#1') == res

    def test_list_adresposities_by_nummer_and_straat(self, crab_gateway,
                                                     crab_service):
        crab_service.ListAdrespositiesByHuisnummer.return_value = Mock(
            AdrespositieItem=[Mock()]
        )
        res = crab_gateway.list_adresposities_by_nummer_and_straat(1, 1)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListAdrespositiesByHuisnummer#11') == res

    def test_list_adresposities_by_subadres(self, crab_gateway, crab_service):
        crab_service.ListAdrespositiesBySubadresId.return_value = Mock(
            AdrespositieItem=[Mock()]
        )
        res = crab_gateway.list_adresposities_by_subadres(1120936)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListAdrespositiesBySubadresId#1120936') == res

    def test_list_adresposities_by_subadres_and_huisnummer(self, crab_gateway,
                                                           crab_service):
        crab_service.ListAdrespositiesBySubadres.return_value = Mock(
            AdrespositieItem=[Mock()]
        )
        res = crab_gateway.list_adresposities_by_subadres_and_huisnummer('A', 129462)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListAdrespositiesBySubadres#A129462') == res
        huisnummer = Huisnummer(129462, None, None, None)
        res = crab_gateway.list_adresposities_by_subadres_and_huisnummer('A', huisnummer)
        assert isinstance(res, list)
        assert crab_gateway.caches['short'].get('ListAdrespositiesBySubadres#A129462') == res

    def test_get_adrespositie_by_id(self, crab_gateway, crab_service):
        crab_service.GetAdrespositieByAdrespositieId.return_value = Mock(
            AdrespositieId=4428005, BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.get_adrespositie_by_id(4428005)
        assert isinstance(res, Adrespositie)
        assert str(crab_gateway.caches['short'].get('GetAdrespositieByAdrespositieId#4428005')) == str(res)

    def test_get_postadres_by_huisnummer(self, crab_gateway, crab_service):
        crab_service.GetPostadresByHuisnummerId.return_value = Mock(
            Postadres='Steenweg op Oosthoven 51, 2300 Turnhout'
        )
        res = crab_gateway.get_postadres_by_huisnummer(1)
        assert res == 'Steenweg op Oosthoven 51, 2300 Turnhout'
        assert str(crab_gateway.caches['short'].get('GetPostadresByHuisnummerId#1')) == str(res)

    def test_get_postadres_by_subadres(self, crab_gateway, crab_service):
        crab_service.GetPostadresBySubadresId.return_value = Mock(
            Postadres='Antoon van Brabantstraat 7 bus B, 2630 Aartselaar'
        )
        res = crab_gateway.get_postadres_by_subadres(1120936)
        assert res == 'Antoon van Brabantstraat 7 bus B, 2630 Aartselaar'
        assert str(crab_gateway.caches['short'].get('GetPostadresBySubadresId#1120936')) == str(res)
