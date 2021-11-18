import six

import pytest
from unittest.mock import Mock

from crabpy.gateway.exception import (
    GatewayRuntimeException,
    GatewayResourceNotFoundException
)
from crabpy.gateway.crab import (
    Gewest, Provincie,
    Gemeente, Deelgemeente, Taal,
    Bewerking, Organisatie,
    Aardsubadres, Aardadres,
    Aardgebouw, Aardwegobject,
    Aardterreinobject, Statushuisnummer,
    Statussubadres, Statusstraatnaam,
    Statuswegsegment, Geometriemethodewegsegment,
    Statusgebouw, Geometriemethodegebouw,
    Herkomstadrespositie, Straat,
    Huisnummer, Postkanton,
    Wegobject, Wegsegment,
    Terreinobject, Perceel,
    Gebouw, Metadata, Subadres,
    Adrespositie
)


class TestCrabGateway:

    def test_list_gewesten(self, crab_gateway, crab_service):
        crab_service.ListGewesten.return_value = Mock(
            GewestItem=[
                Mock(GewestId=1, TaalCodeGewestNaam='NL', GewestNaam='Vlaams')
            ]
        )
        res = crab_gateway.list_gewesten()
        assert isinstance(res, list)
        assert isinstance(res[0], Gewest)

    def test_get_gewest_by_id(self, crab_gateway, crab_service):
        crab_service.GetGewestByGewestIdAndTaalCode.return_value = Mock(
            GewestId=2,
        )
        res = crab_gateway.get_gewest_by_id(2)
        assert isinstance(res, Gewest)
        assert res.id == 2
        assert isinstance(res.centroid, tuple)
        assert isinstance(res.bounding_box, tuple)

    def test_get_gewest_by_unexisting_id(self, crab_gateway, crab_service):
        crab_service.GetGewestByGewestIdAndTaalCode.side_effect = (
            GatewayResourceNotFoundException
        )
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_gewest_by_id(-1)

    def test_list_gemeenten_default(self, crab_gateway, crab_service):
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
        assert isinstance(res[0], Gemeente)
        assert res[0].gewest.id == 2

    def test_list_gemeenten_vlaanderen(self, crab_gateway, crab_service):
        crab_service.ListGemeentenByGewestId.return_value = Mock(
            GemeenteItem=[
                Mock(GemeenteId=1, NISGemeenteCode=10000,
                     TaalCode='NL', TaalCodeGemeenteNaam='NL')
            ]
        )
        gewest = Gewest(2)
        res = crab_gateway.list_gemeenten(gewest)
        assert isinstance(res, list)
        assert isinstance(res[0], Gemeente)
        assert res[0].gewest.id == 2

    def test_list_provincies(self, crab_gateway):
        gewest = Gewest(1)
        res = crab_gateway.list_provincies(gewest)
        assert isinstance(res, list)
        gewest = Gewest(3)
        res = crab_gateway.list_provincies(gewest)
        assert isinstance(res, list)
        gewest = Gewest(2)
        res = crab_gateway.list_provincies(gewest)
        assert isinstance(res, list)
        assert isinstance(res[0], Provincie)
        assert res[0].gewest.id == 2
        gewest = 2
        res = crab_gateway.list_provincies(gewest)
        assert isinstance(res, list)
        assert isinstance(res[0], Provincie)
        assert res[0].gewest.id == 2

    def test_get_provincie_by_id(self, crab_gateway):
        res = crab_gateway.get_provincie_by_id(10000)
        assert isinstance(res, Provincie)
        assert res.niscode == 10000
        res = crab_gateway.get_provincie_by_id(20001)
        assert isinstance(res, Provincie)
        assert res.niscode == 20001
        res = crab_gateway.get_provincie_by_id(20002)
        assert isinstance(res, Provincie)
        assert res.niscode == 20002
        res = crab_gateway.get_provincie_by_id(30000)
        assert isinstance(res, Provincie)
        assert res.niscode == 30000
        res = crab_gateway.get_provincie_by_id(40000)
        assert isinstance(res, Provincie)
        assert res.niscode == 40000
        res = crab_gateway.get_provincie_by_id(50000)
        assert isinstance(res, Provincie)
        assert res.niscode == 50000
        res = crab_gateway.get_provincie_by_id(60000)
        assert isinstance(res, Provincie)
        assert res.niscode == 60000
        res = crab_gateway.get_provincie_by_id(70000)
        assert isinstance(res, Provincie)
        assert res.niscode == 70000
        res = crab_gateway.get_provincie_by_id(80000)
        assert isinstance(res, Provincie)
        assert res.niscode == 80000
        res = crab_gateway.get_provincie_by_id(90000)
        assert isinstance(res, Provincie)
        assert res.niscode == 90000

    def test_get_provincie_by_unexisting_id(self, crab_gateway):
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_provincie_by_id(-1)

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
        provincie = Provincie(10000, 'Antwerpen', Gewest(2))
        res = crab_gateway.list_gemeenten_by_provincie(provincie)
        assert isinstance(res, list)
        assert isinstance(res[0], Gemeente)
        assert str(res[0].niscode)[0] == '1'
        provincie = 10000
        res = crab_gateway.list_gemeenten_by_provincie(provincie)
        assert isinstance(res, list)
        assert isinstance(res[0], Gemeente)
        assert str(res[0].niscode)[0] == '1'

    def test_get_gemeente_by_id(self, crab_gateway, crab_service):
        crab_service.GetGemeenteByGemeenteId.return_value = Mock(
            GemeenteId=1, GewestId=1, BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.get_gemeente_by_id(1)
        assert isinstance(res, Gemeente)
        assert res.id == 1

    def test_get_gemeente_by_id_with_string(self, crab_gateway, crab_service):
        crab_service.GetGemeenteByGemeenteId.side_effect = (
            GatewayRuntimeException(None, None)
        )
        with pytest.raises(GatewayRuntimeException):
            crab_gateway.get_gemeente_by_id('gent')

    def test_get_gemeente_by_unexisting_id(self, crab_gateway, crab_service):
        crab_service.GetGemeenteByGemeenteId.return_value = None
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_gemeente_by_id(-1)

    def test_get_gemeente_by_niscode(self, crab_gateway, crab_service):
        crab_service.GetGemeenteByNISGemeenteCode.return_value = Mock(
            GemeenteId=1, GewestId=1, NisGemeenteCode=11001, BeginBewerking=1,
            BeginOrganisatie=1
        )
        res = crab_gateway.get_gemeente_by_niscode(11001)
        assert isinstance(res, Gemeente)
        assert res.niscode == 11001

    def test_get_gemeente_by_unexisting_niscode(self, crab_gateway, crab_service):
        crab_service.GetGemeenteByNISGemeenteCode.return_value = None
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_gemeente_by_niscode(-1)

    def test_list_deelgemeenten(self, crab_gateway):
        res = crab_gateway.list_deelgemeenten()
        assert isinstance(res, list)
        assert isinstance(res[0], Deelgemeente)

    def test_list_deelgemeenten_wrong_gewest(self, crab_gateway, crab_service):
        with pytest.raises(ValueError):
            crab_gateway.list_deelgemeenten(1)

    def test_list_deelgemeenten_by_gemeente(self, crab_gateway, crab_service):
        crab_service.GetGemeenteByNISGemeenteCode.return_value = Mock(
            GemeenteId=1, GewestId=1, BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.list_deelgemeenten_by_gemeente(45062)
        assert isinstance(res, list)
        assert len(res) == 2
        assert isinstance(res[0], Deelgemeente)
        gemeente = Gemeente(1, None, 45062, None)
        res = crab_gateway.list_deelgemeenten_by_gemeente(gemeente)
        assert isinstance(res, list)
        assert len(res) == 2
        assert isinstance(res[0], Deelgemeente)

    def test_get_deelgemeente_by_id(self, crab_gateway):
        res = crab_gateway.get_deelgemeente_by_id('45062A')
        assert isinstance(res, Deelgemeente)
        assert res.id == '45062A'

    def test_get_deelgemeente_by_unexisting_id(self, crab_gateway):
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_deelgemeente_by_id(-1)

    def test_list_talen(self, crab_gateway, crab_service):
        crab_service.ListTalen.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_talen()
        assert isinstance(res, list)
        assert isinstance(res[0], Taal)

    def test_list_bewerkingen(self, crab_gateway, crab_service):
        res = crab_gateway.list_bewerkingen()
        assert isinstance(res, list)
        assert isinstance(res[0], Bewerking)

    def test_list_organisaties(self, crab_gateway, crab_service):
        res = crab_gateway.list_organisaties()
        assert isinstance(res, list)
        assert isinstance(res[0], Organisatie)

    def test_list_aardsubadressen(self, crab_gateway, crab_service):
        crab_service.ListAardSubadressen.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_aardsubadressen()
        assert isinstance(res, list)
        assert isinstance(res[0], Aardsubadres)

    def test_list_aardadressen(self, crab_gateway, crab_service):
        crab_service.ListAardAdressen.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_aardadressen()
        assert isinstance(res, list)
        assert isinstance(res[0], Aardadres)

    def test_list_aardgebouwen(self, crab_gateway, crab_service):
        crab_service.ListAardGebouwen.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_aardgebouwen()
        assert isinstance(res, list)
        assert isinstance(res[0], Aardgebouw)

    def test_list_aarwegobjecten(self, crab_gateway, crab_service):
        crab_service.ListAardWegobjecten.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_aardwegobjecten()
        assert isinstance(res, list)
        assert isinstance(res[0], Aardwegobject)

    def test_list_aardterreinobjecten(self, crab_gateway, crab_service):
        crab_service.ListAardTerreinobjecten.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_aardterreinobjecten()
        assert isinstance(res, list)
        assert isinstance(res[0], Aardterreinobject)

    def test_list_statushuisnummers(self, crab_gateway, crab_service):
        crab_service.ListStatusHuisnummers.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_statushuisnummers()
        assert isinstance(res, list)
        assert isinstance(res[0], Statushuisnummer)

    def test_list_statussubadressen(self, crab_gateway, crab_service):
        crab_service.ListStatusSubadressen.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_statussubadressen()
        assert isinstance(res, list)
        assert isinstance(res[0], Statussubadres)

    def test_list_statusstraatnamen(self, crab_gateway, crab_service):
        crab_service.ListStatusStraatnamen.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_statusstraatnamen()
        assert isinstance(res, list)
        assert isinstance(res[0], Statusstraatnaam)

    def test_list_statuswegsegmenten(self, crab_gateway, crab_service):
        crab_service.ListStatusWegsegmenten.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_statuswegsegmenten()
        assert isinstance(res, list)
        assert isinstance(res[0], Statuswegsegment)

    def test_list_geometriemethodewegsegmenten(self, crab_gateway,
                                               crab_service):
        crab_service.ListGeometriemethodeWegsegmenten.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_geometriemethodewegsegmenten()
        assert isinstance(res, list)
        assert isinstance(res[0], Geometriemethodewegsegment)

    def test_list_statusgebouwen(self, crab_gateway, crab_service):
        crab_service.ListStatusGebouwen.return_value = Mock(CodeItem=[Mock()])
        res = crab_gateway.list_statusgebouwen()
        assert isinstance(res, list)
        assert isinstance(res[0], Statusgebouw)

    def test_list_gemetriemethodegebouwen(self, crab_gateway, crab_service):
        crab_service.ListGeometriemethodeGebouwen.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_geometriemethodegebouwen()
        assert isinstance(res, list)
        assert isinstance(res[0], Geometriemethodegebouw)

    def test_list_herkomstadrespositie(self, crab_gateway, crab_service):
        crab_service.ListHerkomstAdresposities.return_value = Mock(
            CodeItem=[Mock()]
        )
        res = crab_gateway.list_herkomstadresposities()
        assert isinstance(res, list)
        assert isinstance(res[0], Herkomstadrespositie)

    def test_list_straten(self, crab_gateway, crab_service):
        crab_service.ListStraatnamenWithStatusByGemeenteId.return_value = Mock(
            StraatnaamWithStatusItem=[Mock()]
        )
        res = crab_gateway.list_straten(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Straat)
        gemeente = Gemeente(1, None, None, None)
        res = crab_gateway.list_straten(gemeente)
        assert isinstance(res, list)
        assert isinstance(res[0], Straat)

    def test_list_straten_empty(self, crab_gateway, crab_service):
        crab_service.ListStraatnamenWithStatusByGemeenteId.return_value = Mock(
            StraatnaamWithStatusItem=[]
        )
        res = crab_gateway.list_straten(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_straat_by_id(self, crab_gateway, crab_service):
        crab_service.GetStraatnaamWithStatusByStraatnaamId.return_value = Mock(
            StraatnaamId=1, BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.get_straat_by_id(1)
        assert isinstance(res, Straat)
        assert res.id == 1

    def test_get_straat_by_unexisting_id(self, crab_gateway, crab_service):
        crab_service.GetStraatnaamWithStatusByStraatnaamId.return_value = None
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_straat_by_id(-1)

    def test_list_huisnummers_by_straat(self, crab_gateway, crab_service):
        crab_service.ListHuisnummersWithStatusByStraatnaamId.return_value = (
            Mock(HuisnummerWithStatusItem=[Mock(HuisnummerId=1)])
        )
        res = crab_gateway.list_huisnummers_by_straat(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Huisnummer)
        straat = Straat(1, None, None, None)
        res = crab_gateway.list_huisnummers_by_straat(straat)
        assert isinstance(res, list)
        assert isinstance(res[0], Huisnummer)

    def test_list_huisnummers_by_straat_empty(self, crab_gateway,
                                              crab_service):
        crab_service.ListHuisnummersWithStatusByStraatnaamId.return_value = (
            Mock(HuisnummerWithStatusItem=[])
        )
        res = crab_gateway.list_huisnummers_by_straat(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_list_huisnummers_by_perceel(self, crab_gateway, crab_service):
        crab_service.ListHuisnummersWithStatusByIdentificatorPerceel\
            .return_value = Mock(
                HuisnummerWithStatusItem=[Mock(HuisnummerId=1)]
            )
        crab_service.GetHuisnummerWithStatusByHuisnummerId.return_value = (
            Mock(HuisnummerId=1, BeginBewerking=1, BeginOrganisatie=1)
        )
        res1 = crab_gateway.list_huisnummers_by_perceel("13040C1747/00G002")
        assert isinstance(res1, list)
        assert isinstance(res1[0], Huisnummer)
        perceel = Perceel('13040C1747/00G002')
        res2 = crab_gateway.list_huisnummers_by_perceel(perceel)
        assert isinstance(res2, list)
        assert isinstance(res2[0], Huisnummer)
        assert [p.id for p in res1] == [p.id for p in res2]

    def test_list_huisnummers_by_perceel_empty(self, crab_gateway,
                                               crab_service):
        crab_service.ListHuisnummersWithStatusByIdentificatorPerceel\
            .return_value = Mock(HuisnummerWithStatusItem=[])
        res = crab_gateway.list_huisnummers_by_perceel("13040A0000/00A001")
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_huisnummer_by_id(self, crab_gateway, crab_service):
        crab_service.GetHuisnummerWithStatusByHuisnummerId.return_value = Mock(
            HuisnummerId=1, BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.get_huisnummer_by_id(1)
        assert isinstance(res, Huisnummer)
        assert res.id == 1

    def test_get_huisnummer_by_unexisting_id(self, crab_gateway, crab_service):
        crab_service.GetHuisnummerWithStatusByHuisnummerId.return_value = None
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_huisnummer_by_id(-1)

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
        assert res.huisnummer == '1'
        assert res.straat.id == 1
        straat = Straat(1, None, None, None)
        res = crab_gateway.get_huisnummer_by_nummer_and_straat(1, straat)
        assert isinstance(res, Huisnummer)
        assert res.huisnummer == '1'

    def test_get_huisnummer_by_unexisting_nummer_and_straat(self, crab_gateway,
                                                            crab_service):
        crab_service.GetHuisnummerWithStatusByHuisnummer.return_value = None
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_huisnummer_by_nummer_and_straat(-1, -1)

    def test_list_postkantons_by_gemeente(self, crab_gateway, crab_service):
        crab_service.ListPostkantonsByGemeenteId.return_value = Mock(
            PostkantonItem=[Mock(PostkantonCode=1)]
        )
        res = crab_gateway.list_postkantons_by_gemeente(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Postkanton)
        gemeente = Gemeente(1, None, None, None)
        res = crab_gateway.list_postkantons_by_gemeente(gemeente)
        assert isinstance(res, list)
        assert isinstance(res[0], Postkanton)

    def test_list_postkantons_by_gemeente_empty(self, crab_gateway,
                                                crab_service):
        crab_service.ListPostkantonsByGemeenteId.return_value = Mock(
            PostkantonItem=[]
        )
        res = crab_gateway.list_postkantons_by_gemeente(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_postkanton_by_huisnummer(self, crab_gateway, crab_service):
        crab_service.GetPostkantonByHuisnummerId.return_value = Mock(
            PostkantonCode=1
        )
        res = crab_gateway.get_postkanton_by_huisnummer(1)
        assert isinstance(res, Postkanton)
        huisnummer = Huisnummer(1, None, None, None)
        res = crab_gateway.get_postkanton_by_huisnummer(huisnummer)
        assert isinstance(res, Postkanton)

    def test_get_postkanton_by_unexisting_huisnummer(self, crab_gateway,
                                                     crab_service):
        crab_service.GetPostkantonByHuisnummerId.return_value = None
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_postkanton_by_huisnummer(-1)

    def test_list_wegobjecten_by_straat(self, crab_gateway, crab_service):
        crab_service.ListWegobjectenByStraatnaamId.return_value = Mock(
            WegobjectItem=[Mock(IdentificatorWegobject=1,
                                AardWegobject=1)]
        )
        res = crab_gateway.list_wegobjecten_by_straat(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Wegobject)
        straat = Straat(1, None, None, None)
        res = crab_gateway.list_wegobjecten_by_straat(straat)
        assert isinstance(res, list)
        assert isinstance(res[0], Wegobject)

    def test_list_wegobjecten_by_unexsiting_straat(self, crab_gateway,
                                                   crab_service):
        crab_service.ListWegobjectenByStraatnaamId.return_value = Mock(
            WegobjectItem=[]
        )
        res = crab_gateway.list_wegobjecten_by_straat(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_wegobject_by_id(self, crab_gateway, crab_service):
        crab_service.GetWegobjectByIdentificatorWegobject.return_value = Mock(
            IdentificatorWegobject='53839893', BeginBewerking=1,
            BeginOrganisatie=1
        )
        res = crab_gateway.get_wegobject_by_id("53839893")
        assert isinstance(res, Wegobject)
        assert res.id == "53839893"

    def test_get_wegobject_by_unexisting_id(self, crab_gateway, crab_service):
        crab_service.GetWegobjectByIdentificatorWegobject.return_value = None
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_wegobject_by_id(-1)

    def test_list_wegsegmenten_by_straat(self, crab_gateway, crab_service):
        crab_service.ListWegsegmentenByStraatnaamId.return_value = Mock(
            WegsegmentItem=[Mock()]
        )
        res = crab_gateway.list_wegsegmenten_by_straat(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Wegsegment)
        straat = Straat(1, None, None, None)
        res = crab_gateway.list_wegsegmenten_by_straat(straat)
        assert isinstance(res, list)
        assert isinstance(res[0], Wegsegment)

    def test_list_wegsegmenten_by_straat_empty(self, crab_gateway,
                                               crab_service):
        crab_service.ListWegsegmentenByStraatnaamId.return_value = Mock(
            WegsegmentItem=[]
        )
        res = crab_gateway.list_wegsegmenten_by_straat(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_wegsegment_by_id(self, crab_gateway, crab_service):
        crab_service.GetWegsegmentByIdentificatorWegsegment.return_value = (
            Mock(IdentificatorWegsegment='108724', BeginBewerking=1,
                 BeginOrganisatie=1)
        )
        res = crab_gateway.get_wegsegment_by_id("108724")
        assert isinstance(res, Wegsegment)
        assert res.id == "108724"

    def test_get_wegsegment_by_unexisting_id(self, crab_gateway, crab_service):
        crab_service.GetWegsegmentByIdentificatorWegsegment.return_value = None
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_wegsegment_by_id(-1)

    def test_list_terreinobjecten_by_huisnummer(self, crab_gateway,
                                                crab_service):
        crab_service.ListTerreinobjectenByHuisnummerId.return_value = Mock(
            TerreinobjectItem=[Mock()]
        )
        res = crab_gateway.list_terreinobjecten_by_huisnummer(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Terreinobject)
        huisnummer = Huisnummer(1, None, None, None)
        res = crab_gateway.list_terreinobjecten_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert isinstance(res[0], Terreinobject)

    def test_list_terreinobjecten_by_huisnummer_empty(self, crab_gateway,
                                                      crab_service):
        crab_service.ListTerreinobjectenByHuisnummerId.return_value = Mock(
            TerreinobjectItem=[]
        )
        res = crab_gateway.list_terreinobjecten_by_huisnummer(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_terreinobject_by_id(self, crab_gateway, crab_service):
        crab_service.GetTerreinobjectByIdentificatorTerreinobject\
            .return_value = Mock(
                IdentificatorTerreinobject='13040_C_1747_G_002_00',
                BeginBewerking=1, BeginOrganisatie=1
            )
        res = crab_gateway.get_terreinobject_by_id("13040_C_1747_G_002_00")
        assert isinstance(res, Terreinobject)
        assert res.id == "13040_C_1747_G_002_00"

    def test_get_terreinobject_by_unexisting_id(self, crab_gateway,
                                                crab_service):
        crab_service.GetTerreinobjectByIdentificatorTerreinobject\
            .return_value = None
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_terreinobject_by_id(-1)

    def test_list_percelen_by_huisnummer(self, crab_gateway, crab_service):
        crab_service.ListPercelenByHuisnummerId.return_value = Mock(
            PerceelItem=[Mock()]
        )
        res = crab_gateway.list_percelen_by_huisnummer(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Perceel)
        huisnummer = Huisnummer(1, None, None, None)
        res = crab_gateway.list_percelen_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert isinstance(res[0], Perceel)

    def test_list_percelen_by_huisnummer_empty(self, crab_gateway,
                                               crab_service):
        crab_service.ListPercelenByHuisnummerId.return_value = Mock(
            PerceelItem=[]
        )
        res = crab_gateway.list_percelen_by_huisnummer(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_perceel_by_id(self, crab_gateway, crab_service):
        crab_service.GetPerceelByIdentificatorPerceel.return_value = Mock(
            IdentificatorPerceel='13040C1747/00G002',
            BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.get_perceel_by_id("13040C1747/00G002")
        assert isinstance(res, Perceel)
        assert res.id == "13040C1747/00G002"

    def test_get_perceel_by_unexisting_id(self, crab_gateway, crab_service):
        crab_service.GetPerceelByIdentificatorPerceel.return_value = None
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_perceel_by_id(-1)

    def test_list_gebouwen_by_huisnummer(self, crab_gateway, crab_service):
        crab_service.ListGebouwenByHuisnummerId.return_value = Mock(
            GebouwItem=[Mock(IdentificatorGebouw=1)]
        )
        res = crab_gateway.list_gebouwen_by_huisnummer(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Gebouw)
        huisnummer = Huisnummer(1, None, None, None)
        res = crab_gateway.list_gebouwen_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert isinstance(res[0], Gebouw)

    def test_list_gebouwen_by_huisnummer_empty(self, crab_gateway,
                                               crab_service):
        crab_service.ListGebouwenByHuisnummerId.return_value = Mock(
            GebouwItem=[]
        )
        res = crab_gateway.list_gebouwen_by_huisnummer(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_gebouw_by_id(self, crab_gateway, crab_service):
        crab_service.GetGebouwByIdentificatorGebouw.return_value = Mock(
            IdentificatorGebouw=1538575, BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.get_gebouw_by_id("1538575")
        assert isinstance(res, Gebouw)
        assert res.id == 1538575

    def test_get_gebouw_by_unexisting_id(self, crab_gateway, crab_service):
        crab_service.GetGebouwByIdentificatorGebouw.return_value = None
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_gebouw_by_id(-1)

    def test_list_subadressen_by_huisnummer(self, crab_gateway, crab_service):
        crab_service.ListSubadressenWithStatusByHuisnummerId.return_value = (
            Mock(SubadresWithStatusItem=[Mock(SubadresId=1)])
        )
        res = crab_gateway.list_subadressen_by_huisnummer(129462)
        assert isinstance(res, list)
        assert isinstance(res[0], Subadres)
        huisnummer = Huisnummer(129462, None, None, None)
        res = crab_gateway.list_subadressen_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert isinstance(res[0], Subadres)

    def test_list_subadressen_by_huisnummer_empty(self, crab_gateway,
                                                  crab_service):
        crab_service.ListSubadressenWithStatusByHuisnummerId.return_value = (
            Mock(SubadresWithStatusItem=[])
        )
        res = crab_gateway.list_subadressen_by_huisnummer(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_subadres_by_id(self, crab_gateway, crab_service):
        crab_service.GetSubadresWithStatusBySubadresId.return_value = Mock(
            SubadresId=1120936, BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.get_subadres_by_id(1120936)
        assert isinstance(res, Subadres)
        assert res.id == 1120936

    def test_get_subadres_by_unexisting_id(self, crab_gateway, crab_service):
        crab_service.GetSubadresWithStatusBySubadresId.return_value = None
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_subadres_by_id(-1)

    def test_list_adresposities_by_huisnummer(self, crab_gateway, crab_service):
        crab_service.ListAdrespositiesByHuisnummerId.return_value = Mock(
            AdrespositieItem=[Mock()]
        )
        res = crab_gateway.list_adresposities_by_huisnummer(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Adrespositie)

    def test_list_adresposities_by_huisnummer_empty(self, crab_gateway,
                                                    crab_service):
        crab_service.ListAdrespositiesByHuisnummerId.return_value = Mock(
            AdrespositieItem=[]
        )
        res = crab_gateway.list_adresposities_by_huisnummer(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_list_adresposities_by_nummer_and_straat(self, crab_gateway,
                                                     crab_service):
        crab_service.ListAdrespositiesByHuisnummer.return_value = Mock(
            AdrespositieItem=[Mock()]
        )
        res = crab_gateway.list_adresposities_by_nummer_and_straat(1, 1)
        assert isinstance(res, list)
        assert isinstance(res[0], Adrespositie)

    def test_list_adresposities_by_nummer_and_straat_empty(self, crab_gateway,
                                                           crab_service):
        crab_service.ListAdrespositiesByHuisnummer.return_value = Mock(
            AdrespositieItem=[]
        )
        res = crab_gateway.list_adresposities_by_nummer_and_straat(0, 0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_list_adresposities_by_subadres(self, crab_gateway, crab_service):
        crab_service.ListAdrespositiesBySubadresId.return_value = Mock(
            AdrespositieItem=[Mock()]
        )
        res = crab_gateway.list_adresposities_by_subadres(1120936)
        assert isinstance(res, list)
        assert isinstance(res[0], Adrespositie)

    def test_list_adresposities_by_subadres_empty(self, crab_gateway,
                                                  crab_service):
        crab_service.ListAdrespositiesBySubadresId.return_value = Mock(
            AdrespositieItem=[]
        )
        res = crab_gateway.list_adresposities_by_subadres(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_list_adresposities_by_subadres_and_huisnummer(self, crab_gateway,
                                                           crab_service):
        crab_service.ListAdrespositiesBySubadres.return_value = Mock(
            AdrespositieItem=[Mock()]
        )
        res = crab_gateway.list_adresposities_by_subadres_and_huisnummer('A', 129462)
        assert isinstance(res, list)
        assert isinstance(res[0], Adrespositie)

    def test_list_adresposities_by_unexisting_subadres_and_huisnummer(
            self, crab_gateway, crab_service):
        crab_service.ListAdrespositiesBySubadres.return_value = Mock(
            AdrespositieItem=[]
        )
        res = crab_gateway.list_adresposities_by_subadres_and_huisnummer(0, 0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_adrespositie_by_id(self, crab_gateway, crab_service):
        crab_service.GetAdrespositieByAdrespositieId.return_value = Mock(
            AdrespositieId=4428005, BeginBewerking=1, BeginOrganisatie=1
        )
        res = crab_gateway.get_adrespositie_by_id(4428005)
        assert isinstance(res, Adrespositie)
        assert res.id == 4428005

    def test_get_adrespositie_by_unexisting_id(self, crab_gateway,
                                               crab_service):
        crab_service.GetAdrespositieByAdrespositieId.return_value = None
        with pytest.raises(GatewayResourceNotFoundException):
            crab_gateway.get_adrespositie_by_id(-1)

    def test_get_postadres_by_huisnummer(self, crab_gateway, crab_service):
        crab_service.GetPostadresByHuisnummerId.return_value = Mock(
            Postadres='Steenweg op Oosthoven 51, 2300 Turnhout'
        )
        res = crab_gateway.get_postadres_by_huisnummer(1)
        assert res == 'Steenweg op Oosthoven 51, 2300 Turnhout'
        hnr = Huisnummer(1, None, None, None)
        res = crab_gateway.get_postadres_by_huisnummer(hnr)
        assert res == 'Steenweg op Oosthoven 51, 2300 Turnhout'

    def test_get_postadres_by_subadres(self, crab_gateway, crab_service):
        crab_service.GetPostadresBySubadresId.return_value = Mock(
            Postadres='Antoon van Brabantstraat 7 bus B, 2630 Aartselaar'
        )
        res = crab_gateway.get_postadres_by_subadres(1120936)
        assert res == 'Antoon van Brabantstraat 7 bus B, 2630 Aartselaar'
        subadres = Subadres(1120936, None, None)
        res = crab_gateway.get_postadres_by_subadres(subadres)
        assert res == 'Antoon van Brabantstraat 7 bus B, 2630 Aartselaar'


class TestGewest:

    def test_fully_initialised(self):
        g = Gewest(
            2,
            {'nl': 'Vlaams gewest', 'fr': 'Région Flamande'},
            (138165.09, 189297.53),
            (22279.17, 153050.23, 258873.3, 244022.31)
        )
        assert g.id == 2
        assert g.naam =='Vlaams gewest'
        assert g.centroid == (138165.09, 189297.53)
        assert g.bounding_box == (22279.17, 153050.23, 258873.3, 244022.31)
        assert 'Vlaams gewest (2)' == str(g)
        assert "Gewest(2)" == repr(g)

    def test_str_and_repr_dont_lazy_load(self):
        g = Gewest(2)
        assert 'Gewest 2' == str(g)
        assert 'Gewest(2)'== repr(g)

    def test_check_gateway_not_set(self):
        g = Gewest(2)
        with pytest.raises(RuntimeError):
            g.check_gateway()

    def test_gemeenten(self, crab_gateway, crab_service):
        crab_service.GetGewestByGewestIdAndTaalCode.return_value = Mock(
            GewestId=2,
        )
        crab_service.ListGemeentenByGewestId.return_value = Mock(
            GemeenteItem=[
                Mock(GemeenteId=1, NISGemeenteCode=10000,
                     TaalCode='NL', TaalCodeGemeenteNaam='NL')
            ]
        )
        g = Gewest(2)
        g.set_gateway(crab_gateway)
        gemeenten = g.gemeenten
        assert isinstance(gemeenten, list)

    def test_provincies(self, crab_gateway):
        g = Gewest(2)
        g.set_gateway(crab_gateway)
        provincies = g.provincies
        assert isinstance(provincies, list)
        assert len(provincies) == 5

    def test_lazy_load(self, crab_gateway, crab_service):
        crab_service.GetGewestByGewestIdAndTaalCode.return_value = Mock(
            GewestId=2, GewestNaam='Vlaams Gewest', CenterX=138165.09,
            CenterY=189297.53, MinimumX=22279.17, MinimumY=153050.23,
            MaximumX=258873.3, MaximumY=244022.31
        )
        g = Gewest(2)
        g.set_gateway(crab_gateway)
        assert g.id == 2
        assert str(g.naam) == 'Vlaams Gewest'
        assert g.centroid == (138165.09, 189297.53)
        assert g.bounding_box == (22279.17, 153050.23, 258873.3, 244022.31)


class TestProvincie:

    def test_fully_initialised(self):
        p = Provincie(20001, 'Vlaams-Brabant', Gewest(2))
        assert p.niscode == 20001
        assert p.naam == 'Vlaams-Brabant'
        assert 'Vlaams-Brabant (20001)' == str(p)
        assert "Provincie(20001, 'Vlaams-Brabant', Gewest(2))" == repr(p)

    def test_check_gateway_not_set(self):
        p = Provincie(20001, 'Vlaams-Brabant', Gewest(2))
        with pytest.raises(RuntimeError):
            p.check_gateway()

    def test_gemeenten(self, crab_gateway, crab_service):
        crab_service.GetGewestByGewestIdAndTaalCode.return_value = Mock(
            GewestId=2
        )
        crab_service.ListGemeentenByGewestId.return_value = Mock(
            GemeenteItem=[
                Mock(GemeenteId=1, NISGemeenteCode=10000,
                     TaalCode='NL', TaalCodeGemeenteNaam='NL')
            ]
        )
        p = Provincie(20001, 'Vlaams-Brabant', Gewest(2))
        p.set_gateway(crab_gateway)
        gemeenten = p.gemeenten
        assert isinstance(gemeenten, list)


class TestGemeente:

    def test_fully_initialised(self):
        g = Gemeente(
            1,
            'Aartselaar',
            11001,
            Gewest(2),
            Taal('nl', 'Nederlands', 'Nederlands.'),
            (150881.07, 202256.84),
            (148950.36, 199938.28, 152811.77, 204575.39),
            Metadata(
                '1830-01-01 00:00:00',
                '2002-08-13 17:32:32',
                Bewerking(1, '', ''),
                Organisatie(6, '', '')
            )
        )
        assert g.id == 1
        assert g.naam == 'Aartselaar'
        assert g.niscode == 11001
        assert isinstance(g.gewest, Gewest)
        assert g.gewest.id == 2
        assert g.centroid == (150881.07, 202256.84)
        assert g.bounding_box == (148950.36, 199938.28, 152811.77, 204575.39)
        assert int(g.gewest.id) ==2
        assert isinstance(g._taal, Taal)
        assert g._taal_id == 'nl'
        assert isinstance(g.metadata, Metadata)
        assert g.metadata.begin_datum == '1830-01-01 00:00:00'
        assert g.metadata.begin_tijd == '2002-08-13 17:32:32'
        assert isinstance(g.metadata.begin_bewerking, Bewerking)
        assert int(g.metadata.begin_bewerking.id) == 1
        assert isinstance(g.metadata.begin_organisatie, Organisatie)
        assert int(g.metadata.begin_organisatie.id) == 6
        assert 'Aartselaar (1)' == str(g)
        assert "Gemeente(1, 'Aartselaar', 11001)" == repr(g)

    @pytest.mark.skipif(
        not six.PY2,
        reason='This test only works on python 2.x'
    )
    def test_unicode_py2(self):
        g = Gemeente(92, 'Biévène', 23009, Gewest(2))
        assert 'Biévène (92)'.encode() == str(g)

    @pytest.mark.skipif(
        not six.PY3,
        reason='This test only works on python 3.x'
    )
    def test_unicode_py3(self):
        g = Gemeente(92, 'Biévène', 23009, Gewest(2))
        assert 'Biévène (92)' == str(g)

    def test_str_and_repr_dont_lazy_load(self):
        g = Gemeente(1, 'Aartselaar', 11001, Gewest(2))
        assert 'Aartselaar (1)' == str(g)
        assert "Gemeente(1, 'Aartselaar', 11001)" == repr(g)

    def test_check_gateway_not_set(self):
        g = Gemeente(1, 'Aartselaar', 11001, Gewest(2))
        with pytest.raises(RuntimeError):
            g.check_gateway()

    def test_lazy_load(self, crab_gateway, crab_service):
        crab_service.ListTalen.return_value = Mock(CodeItem=[Mock(Code='nl')])
        crab_service.GetGemeenteByGemeenteId.return_value = Mock(
            GemeenteId=1, GewestId=1, BeginBewerking=1, BeginOrganisatie=1,
            CenterX=150881.07, CenterY=202256.84, MinimumX=148950.36,
            MinimumY=199938.28, MaximumX=152811.77, MaximumY=204575.39,
            TaalCode='nl'
        )
        g = Gemeente(1, 'Aartselaar', 11001, Gewest(2))
        g.set_gateway(crab_gateway)
        assert g.id == 1
        assert g.naam == 'Aartselaar'
        assert g.niscode == 11001
        assert isinstance(g.gewest, Gewest)
        assert int(g.gewest.id) == 2
        assert g.taal.id == 'nl'
        assert g.centroid == (150881.07, 202256.84)
        assert g.bounding_box == (148950.36, 199938.28, 152811.77, 204575.39)
        g.metadata.set_gateway(crab_gateway)
        assert isinstance(g.metadata, Metadata)
        assert not g.metadata.begin_datum == None
        assert not g.metadata.begin_tijd == None
        assert isinstance(g.metadata.begin_bewerking, Bewerking)
        assert int(g.metadata.begin_bewerking.id) == 1
        assert isinstance(g.metadata.begin_organisatie, Organisatie)
        assert int(g.metadata.begin_organisatie.id) == 1

    def test_straten(self, crab_gateway, crab_service):
        crab_service.ListStraatnamenWithStatusByGemeenteId.return_value = Mock(
            StraatnaamWithStatusItem=[Mock()]
        )
        g = Gemeente(1, 'Aartselaar', 11001, Gewest(3))
        g.set_gateway(crab_gateway)
        straten = g.straten
        assert isinstance(straten, list)

    def test_postkantons(self, crab_gateway, crab_service):
        crab_service.ListPostkantonsByGemeenteId.return_value = Mock(
            PostkantonItem=[Mock(PostkantonCode=1)]
        )
        g = Gemeente(1, 'Aartselaar', 11001, Gewest(3))
        g.set_gateway(crab_gateway)
        postkanton = g.postkantons
        assert isinstance(postkanton, list)

    def test_provincie(self, crab_gateway):
        g = Gemeente(1, 'Aartselaar', 11001, Gewest(2))
        g.set_gateway(crab_gateway)
        provincie = g.provincie
        assert isinstance(provincie, Provincie)
        assert 10000 == provincie.id


class TestDeelgemeente:

    def test_fully_initialised(self):
        dg = Deelgemeente('45062A', 'Sint-Maria-Horebeke', 45062)
        assert dg.id == '45062A'
        assert dg.naam == 'Sint-Maria-Horebeke'
        assert 'Sint-Maria-Horebeke (45062A)' == str(dg)
        assert "Deelgemeente('45062A', 'Sint-Maria-Horebeke', 45062)" == repr(dg)

    def test_check_gateway_not_set(self):
        dg = Deelgemeente('45062A', 'Sint-Maria-Horebeke', 45062)
        with pytest.raises(RuntimeError):
            dg.check_gateway()

    def test_gemeente(self, crab_gateway, crab_service):
        crab_service.GetGemeenteByNISGemeenteCode.return_value = Mock(
            GemeenteId=1, GewestId=1, NisGemeenteCode=45062, BeginBewerking=1,
            BeginOrganisatie=1, GemeenteNaam='Horebeke'
        )
        dg = Deelgemeente('45062A', 'Sint-Maria-Horebeke', 45062)
        dg.set_gateway(crab_gateway)
        gemeente = dg.gemeente
        assert isinstance(gemeente, Gemeente)
        assert gemeente.niscode == 45062
        assert gemeente.naam == 'Horebeke'


class TestTaal:
    def test_fully_initialised(self):
        t = Taal(
            "nl",
            'Nederlands',
            'Nederlands.'
        )
        assert t.id == "nl"
        assert t.naam == 'Nederlands'
        assert t.definitie == 'Nederlands.'
        assert 'Nederlands' == str(t)
        assert "Taal('nl', 'Nederlands', 'Nederlands.')" == repr(t)


class TestBewerking:
    def test_repr(self):
        b = Bewerking(
            '3',
            'correctie',
            'Correctie van de attributen.'
        )
        assert "Bewerking(3, 'correctie', 'Correctie van de attributen.')" == repr(b)


class TestOrganisatie:
    def test_repr(self):
        o = Organisatie(
            '6',
            'NGI',
            'Nationaal Geografisch Instituut.'
        )
        assert "Organisatie(6, 'NGI', 'Nationaal Geografisch Instituut.')" == repr(o)


class TestAardsubadres:
    def test_repr(self):
        a = Aardsubadres(
            '1',
            'appartementNummer',
            'Nummer van het appartement.'
        )
        assert "Aardsubadres(1, 'appartementNummer', 'Nummer van het appartement.')" == repr(a)


class TestAardadres:
    def test_repr(self):
        a = Aardadres(
            '1',
            'subAdres',
            'Aanduiding van een plaats op een huisnummer'
        )
        assert "Aardadres(1, 'subAdres', 'Aanduiding van een plaats op een huisnummer')" == repr(a)


class TestAardgebouw:
    def test_repr(self):
        a = Aardgebouw(
            '3',
            'virtueel gebouw',
            'gbg afgezoomd met virtuele gvl'
        )
        assert "Aardgebouw(3, 'virtueel gebouw', 'gbg afgezoomd met virtuele gvl')" == repr(a)


class TestAardwegobject:
    def test_repr(self):
        a = Aardwegobject(
            '1',
            'taTEL',
            'Wegverbinding volgens TeleAtlas.'
        )
        assert "Aardwegobject(1, 'taTEL', 'Wegverbinding volgens TeleAtlas.')" == repr(a)


class TestAardterreinobject:
    def test_repr(self):
        a = Aardterreinobject(
            '1',
            'kadPerceel',
            'Perceel volgens het Kadaster.'
        )
        assert "Aardterreinobject(1, 'kadPerceel', 'Perceel volgens het Kadaster.')" == repr(a)


class TestStatushuisnummer:
    def test_repr(self):
        s = Statushuisnummer(
            '1',
            'voorgesteld',
            None
        )
        assert "Statushuisnummer(1, 'voorgesteld', 'None')" == repr(s)


class TestStatussubadres:
    def test_repr(self):
        s = Statussubadres(
            '1',
            'voorgesteld',
            None
        )
        assert "Statussubadres(1, 'voorgesteld', 'None')" == repr(s)


class TestStatusstraatnaam:
    def test_repr(self):
        s = Statusstraatnaam(
            '1',
            'voorgesteld',
            None
        )
        assert "Statusstraatnaam(1, 'voorgesteld', 'None')" == repr(s)


class TestStatuswegsegment:
    def test_repr(self):
        s = Statuswegsegment(
            '1',
            'vergunningAangevraagd',
            None
        )
        assert "Statuswegsegment(1, 'vergunningAangevraagd', 'None')" == repr(s)


class TestGeometriemethodewegsegment:
    def test_repr(self):
        g = Geometriemethodewegsegment(
            '2',
            'opmeting',
            None
        )
        assert "Geometriemethodewegsegment(2, 'opmeting', 'None')" == repr(g)


class TestStatusgebouw:
    def test_repr(self):
        s = Statusgebouw(
            '1',
            'vergunningAangevraagd',
            None
        )
        assert "Statusgebouw(1, 'vergunningAangevraagd', 'None')" == repr(s)


class TestGeometriemethodegebouw:
    def test_repr(self):
        g = Geometriemethodegebouw(
            '2',
            'opmeting',
            None
        )
        assert "Geometriemethodegebouw(2, 'opmeting', 'None')" == repr(g)


class TestHerkomstadrespositie:
    def test_repr(self):
        h = Herkomstadrespositie(
            '6',
            'manueleAanduidingVanToegangTotDeWeg',
            None
        )
        assert "Herkomstadrespositie(6, 'manueleAanduidingVanToegangTotDeWeg', 'None')" == repr(h)


class TestStraat:
    def test_fully_initialised(self):
        s = Straat(
            1,
            'Acacialaan',
            1,
            Statusstraatnaam(3, 'inGebruik', None),
            'Acacialaan', 'nl', None, None,
            Metadata(
                '1830-01-01 00:00:00',
                '2013-04-12 20:07:25.960000',
                Bewerking(3, '', ''),
                Organisatie(1, '', '')
            )
        )
        assert s.id == 1
        assert s.label == 'Acacialaan'
        assert s.namen == (('Acacialaan', 'nl'), (None, None))
        assert int(s.status_id) == 3
        assert isinstance(s.status, Statusstraatnaam)
        assert int(s.gemeente_id) == 1
        assert isinstance(s.metadata, Metadata)
        assert s.metadata.begin_datum == '1830-01-01 00:00:00'
        assert s.metadata.begin_tijd == '2013-04-12 20:07:25.960000'
        assert isinstance(s.metadata.begin_bewerking, Bewerking)
        assert int(s.metadata.begin_bewerking.id) == 3
        assert isinstance(s.metadata.begin_organisatie, Organisatie)
        assert int(s.metadata.begin_organisatie.id) == 1
        assert 'Acacialaan (1)' == str(s)
        assert "Straat(1, 'Acacialaan', 1, 3)" == repr(s)

    def test_lazy_load(self, crab_gateway, crab_service):
        crab_service.ListStatusStraatnamen.return_value = Mock(
            CodeItem=[Mock(Code=3)]
        )
        crab_service.GetStraatnaamWithStatusByStraatnaamId.return_value = Mock(
            StraatnaamId=1, BeginBewerking=1, BeginOrganisatie=1,
            StraatnaamLabel='Acacialaan', Straatnaam='Acacialaan',
            TaalCode='nl', StraatnaamTweedeTaal=None, TaalCodeTweedeTaal=None
        )
        crab_service.GetGemeenteByGemeenteId.return_value = Mock(
            GemeenteId=1, GewestId=1, BeginBewerking=1, BeginOrganisatie=1
        )
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab_gateway)
        assert s.id == 1
        assert s.label == 'Acacialaan'
        assert int(s.status.id) == 3
        assert s.namen == (('Acacialaan', 'nl'), (None, None))
        assert int(s.gemeente.id) == 1
        s.metadata.set_gateway(crab_gateway)
        assert isinstance(s.metadata, Metadata)
        assert s.metadata.begin_datum is not None
        assert s.metadata.begin_tijd is not None
        assert isinstance(s.metadata.begin_bewerking, Bewerking)
        assert int(s.metadata.begin_bewerking.id) == 1
        assert isinstance(s.metadata.begin_organisatie, Organisatie)
        assert int(s.metadata.begin_organisatie.id) == 1

    def test_str_and_repr_dont_lazy_load(self):
        s = Straat(1, 'Acacialaan', 1, 3)
        assert 'Acacialaan (1)' == str(s)
        assert "Straat(1, 'Acacialaan', 1, 3)" == repr(s)

    def test_check_gateway_not_set(self):
        s = Straat(1, 'Acacialaan', 1, 3)
        with pytest.raises(RuntimeError):
            s.check_gateway()

    def test_huisnummers(self, crab_gateway, crab_service):
        crab_service.ListHuisnummersWithStatusByStraatnaamId.return_value = (
            Mock(HuisnummerWithStatusItem=[Mock(HuisnummerId=1)])
        )
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab_gateway)
        huisnummers = s.huisnummers
        assert isinstance(huisnummers, list)

    def test_taal(self, crab_gateway, crab_service):
        crab_service.ListTalen.return_value = Mock(CodeItem=[Mock(Code='nl')])
        crab_service.GetStraatnaamWithStatusByStraatnaamId.return_value = Mock(
            StraatnaamId=1, BeginBewerking=1, BeginOrganisatie=1,
            StraatnaamLabel='Acacialaan', Straatnaam='Acacialaan',
            TaalCode='nl', StraatnaamTweedeTaal=None, TaalCodeTweedeTaal=None
        )
        crab_service.GetGemeenteByGemeenteId.return_value = Mock(
            GemeenteId=1, GewestId=1, BeginBewerking=1, BeginOrganisatie=1,
            TaalCode='nl'
        )
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab_gateway)
        taal = s.taal
        assert isinstance(taal, Taal)
        assert s.taal.id == 'nl'

    def test_gemeente(self, crab_gateway, crab_service):
        crab_service.GetGemeenteByGemeenteId.return_value = Mock(
            GemeenteId=1, GewestId=1, BeginBewerking=1, BeginOrganisatie=1
        )
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab_gateway)
        gemeente = s.gemeente
        assert isinstance(gemeente, Gemeente)

    def test_status(self, crab_gateway, crab_service):
        crab_service.ListStatusStraatnamen.return_value = Mock(
            CodeItem=[Mock(Code=3)]
        )
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab_gateway)
        status = s.status
        assert isinstance(status, Statusstraatnaam)

    def test_wegobjecten(self, crab_gateway, crab_service):
        crab_service.ListWegobjectenByStraatnaamId.return_value = Mock(
            WegobjectItem=[Mock(IdentificatorWegobject=1,
                                AardWegobject=1)]
        )
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab_gateway)
        wegobjecten = s.wegobjecten
        assert isinstance(wegobjecten, list)
        assert isinstance(wegobjecten[0], Wegobject)

    def test_wegsegmenten(self, crab_gateway, crab_service):
        crab_service.ListWegsegmentenByStraatnaamId.return_value = Mock(
            WegsegmentItem=[Mock()]
        )
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab_gateway)
        wegsegmenten = s.wegsegmenten
        assert isinstance(wegsegmenten, list)
        assert isinstance(wegsegmenten[0], Wegsegment)

    def test_bounding_box(self, crab_gateway, crab_service):
        crab_service.ListWegsegmentenByStraatnaamId.return_value = Mock(
            WegsegmentItem=[Mock()]
        )
        crab_service.GetWegsegmentByIdentificatorWegsegment.return_value = (
            Mock(IdentificatorWegsegment='108724', BeginBewerking=1,
                 BeginOrganisatie=1,
                 Geometrie='LINESTRING (150339.255243488 201166.401677653,'
                           '150342.836939491 201165.832525652,'
                           '150345.139531493 201165.466573652,'
                           '150349.791371495 201164.769421652)')
        )
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab_gateway)
        bounding = s.bounding_box
        assert isinstance(bounding, list)
        assert len(bounding) == 4


class TestHuisnummer:
    def test_fully_initialised(self):
        h = Huisnummer(
            1,
            Statushuisnummer(3, 'inGebruik', None),
            "51",
            17718,
            Metadata(
                '1830-01-01 00:00:00',
                '2011-04-29 13:27:40.230000',
                Bewerking(1, '', ''),
                Organisatie(5, '', '')
            )
        )
        assert h.id == 1
        assert h.huisnummer == "51"
        assert int(h.status_id) == 3
        assert isinstance(h.status, Statushuisnummer)
        assert int(h.straat_id) == 17718
        assert isinstance(h.metadata, Metadata)
        assert h.metadata.begin_datum == '1830-01-01 00:00:00'
        assert h.metadata.begin_tijd, '2011-04-29 13:27:40.230000'
        assert isinstance(h.metadata.begin_bewerking, Bewerking)
        assert int(h.metadata.begin_bewerking.id) == 1
        assert isinstance(h.metadata.begin_organisatie, Organisatie)
        assert int(h.metadata.begin_organisatie.id) == 5
        assert '51 (1)' == str(h)
        assert "Huisnummer(1, 3, '51', 17718)" == repr(h)

    def test_str_dont_lazy_load(self):
        h = Huisnummer(1, 3, '51', 17718)
        assert '51 (1)' == str(h)

    def test_lazy_load(self, crab_gateway, crab_service):
        crab_service.ListStatusHuisnummers.return_value = Mock(
            CodeItem=[Mock(Code=3)]
        )
        crab_service.GetStraatnaamWithStatusByStraatnaamId.return_value = Mock(
            StraatnaamId=17718, BeginBewerking=1, BeginOrganisatie=1
        )
        crab_service.GetHuisnummerWithStatusByHuisnummerId.return_value = Mock(
            HuisnummerId=1, BeginBewerking=1, BeginOrganisatie=1
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab_gateway)
        assert h.id == 1
        assert int(h.status.id) == 3
        assert h.huisnummer == "51"
        assert int(h.straat.id) == 17718
        h.metadata.set_gateway(crab_gateway)
        assert isinstance(h.metadata, Metadata)
        assert not h.metadata.begin_datum == None
        assert not h.metadata.begin_tijd == None
        assert isinstance(h.metadata.begin_bewerking, Bewerking)
        assert int(h.metadata.begin_bewerking.id) == 1
        assert isinstance(h.metadata.begin_organisatie, Organisatie)
        assert int(h.metadata.begin_organisatie.id) == 1

    def test_postkanton(self, crab_gateway, crab_service):
        crab_service.GetPostkantonByHuisnummerId.return_value = Mock(
            PostkantonCode=1
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab_gateway)
        postkanton = h.postkanton
        assert isinstance(postkanton, Postkanton)

    def test_terreinobjecten(self, crab_gateway, crab_service):
        crab_service.ListTerreinobjectenByHuisnummerId.return_value = Mock(
            TerreinobjectItem=[Mock()]
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab_gateway)
        terreinobjecten = h.terreinobjecten
        assert isinstance(terreinobjecten, list)

    def test_percelen(self, crab_gateway, crab_service):
        crab_service.ListPercelenByHuisnummerId.return_value = Mock(
            PerceelItem=[Mock()]
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab_gateway)
        percelen = h.percelen
        assert isinstance(percelen, list)

    def test_gebouwen(self, crab_gateway, crab_service):
        crab_service.ListGebouwenByHuisnummerId.return_value = Mock(
            GebouwItem=[Mock(IdentificatorGebouw=1)]
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab_gateway)
        gebouwen = h.gebouwen
        assert isinstance(gebouwen, list)

    def test_subadressen(self, crab_gateway, crab_service):
        crab_service.ListSubadressenWithStatusByHuisnummerId.return_value = (
            Mock(SubadresWithStatusItem=[Mock(SubadresId=1)])
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab_gateway)
        subadressen = h.subadressen
        assert isinstance(subadressen, list)

    def test_adresposities(self, crab_gateway, crab_service):
        crab_service.ListAdrespositiesByHuisnummerId.return_value = Mock(
            AdrespositieItem=[Mock()]
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab_gateway)
        adresposities = h.adresposities
        assert isinstance(adresposities, list)

    def test_status(self, crab_gateway, crab_service):
        crab_service.ListStatusHuisnummers.return_value = Mock(
            CodeItem=[Mock(Code=3)]
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab_gateway)
        status = h.status
        assert isinstance(status, Statushuisnummer)

    def test_bounding_box(self, crab_gateway, crab_service):
        crab_service.ListTerreinobjectenByHuisnummerId.return_value = Mock(
            TerreinobjectItem=[Mock()]
        )
        crab_service.GetTerreinobjectByIdentificatorTerreinobject\
            .return_value = Mock(
                IdentificatorTerreinobject='13040_C_1747_G_002_00',
                BeginBewerking=1, BeginOrganisatie=1
            )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab_gateway)
        bounding = h.bounding_box
        assert isinstance(bounding, list)
        assert len(bounding) == 4

    def test_check_gateway_not_set(self):
        h = Huisnummer(1, 3, '51', 17718)
        with pytest.raises(RuntimeError):
            h.check_gateway()

    def test_postadres(self, crab_gateway, crab_service):
        crab_service.GetPostadresByHuisnummerId.return_value = Mock(
            Postadres='Steenweg op Oosthoven 51, 2300 Turnhout'
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab_gateway)
        assert h.postadres == 'Steenweg op Oosthoven 51, 2300 Turnhout'


class TestPostkanton:
    def test_fully_initialised(self):
        p = Postkanton(
            2630
        )
        assert p.id == 2630
        assert 'Postkanton 2630' == str(p)
        assert 'Postkanton(2630)' == repr(p)


class TestWegobject:
    def test_fully_initialised(self):
        w = Wegobject(
            "53839893",
            Aardwegobject(4, 'ntLink', 'Wegverbinding volgens NavTeq.'),
            (150753.46, 200148.41),
            (150693.58, 200080.56, 150813.35, 200216.27),
            Metadata(
                '1830-01-01 00:00:00',
                '2008-04-17 16:32:11.753000',
                Bewerking(1, '', ''),
                Organisatie(8, '', '')
            )
        )
        assert w.id == "53839893"
        assert w.centroid == (150753.46, 200148.41)
        assert w.bounding_box == (150693.58, 200080.56, 150813.35, 200216.27)
        assert int(w.aard_id) == 4
        assert isinstance(w.aard, Aardwegobject)
        assert isinstance(w.metadata, Metadata)
        assert w.metadata.begin_datum == '1830-01-01 00:00:00'
        assert w.metadata.begin_tijd == '2008-04-17 16:32:11.753000'
        assert isinstance(w.metadata.begin_bewerking, Bewerking)
        assert int(w.metadata.begin_bewerking.id) == 1
        assert isinstance(w.metadata.begin_organisatie, Organisatie)
        assert int(w.metadata.begin_organisatie.id) == 8
        assert 'Wegobject 53839893' == str(w)
        assert 'Wegobject(53839893)' == repr(w)

    def test_check_gateway_not_set(self):
        w = Wegobject(1, 4)
        with pytest.raises(RuntimeError):
            w.check_gateway()

    def test_aard(self, crab_gateway, crab_service):
        crab_service.ListAardWegobjecten.return_value = Mock(
            CodeItem=[Mock(Code=4)]
        )
        w = Wegobject("53839893", 4)
        w.set_gateway(crab_gateway)
        aard = w.aard
        assert isinstance(aard, Aardwegobject)

    def test_lazy_load(self, crab_gateway, crab_service):
        crab_service.ListAardWegobjecten.return_value = Mock(
            CodeItem=[Mock(Code=4)]
        )
        crab_service.GetWegobjectByIdentificatorWegobject.return_value = Mock(
            IdentificatorWegobject='53839893', BeginBewerking=1,
            BeginOrganisatie=1, CenterX=150753.46, CenterY=200148.41,
            MinimumX=150693.58, MinimumY=200080.56, MaximumX=150813.35,
            MaximumY=200216.27
        )
        w = Wegobject("53839893", 4)
        w.set_gateway(crab_gateway)
        assert w.id == "53839893"
        assert int(w.aard.id) == 4
        assert w.centroid == (150753.46, 200148.41)
        assert w.bounding_box == (150693.58, 200080.56, 150813.35, 200216.27)
        w.metadata.set_gateway(crab_gateway)
        assert isinstance(w.metadata, Metadata)
        assert not w.metadata.begin_datum == None
        assert not w.metadata.begin_tijd == None
        assert isinstance(w.metadata.begin_bewerking, Bewerking)
        assert int(w.metadata.begin_bewerking.id) == 1
        assert isinstance(w.metadata.begin_organisatie, Organisatie)
        assert int(w.metadata.begin_organisatie.id) == 1


class TestWegsegment:
    def test_fully_initialised(self):
        w = Wegsegment(
            "108724",
            Statuswegsegment(4, 'inGebruik', None),
            Geometriemethodewegsegment(3, 'grb', None),
            """LINESTRING (150339.255243488 201166.401677653,\
 150342.836939491 201165.832525652,\
 150345.139531493 201165.466573652,\
 150349.791371495 201164.769421652,\
 150352.512459494 201164.36161365,\
 150358.512331501 201163.46241365,\
 150375.039179511 201156.606669646,\
 150386.901963517 201150.194893643,\
 150397.470027529 201142.865485638,\
 150403.464011535 201135.266637631,\
 150407.825739533 201127.481037624,\
 150414.301515542 201109.016653612,\
 150431.792971551 201057.519821577,\
 150442.85677956 201026.858701557,\
 150454.530123569 200999.312717538,\
 150472.404939577 200955.342029508,\
 150483.516619585 200927.052237488,\
 150500.807755597 200883.890765458,\
 150516.94650761 200844.146253429,\
 150543.214411631 200773.35943738,\
 150546.079307631 200764.489805374,\
 150548.592075631 200754.511565369)""",
            Metadata(
                '1830-01-01 00:00:00',
                '2013-04-12 20:12:12.687000',
                Bewerking(3, '', ''),
                Organisatie(1, '', '')
            )
        )
        assert w.id == "108724"
        assert w.geometrie == """LINESTRING (150339.255243488 201166.401677653,\
 150342.836939491 201165.832525652,\
 150345.139531493 201165.466573652,\
 150349.791371495 201164.769421652,\
 150352.512459494 201164.36161365,\
 150358.512331501 201163.46241365,\
 150375.039179511 201156.606669646,\
 150386.901963517 201150.194893643,\
 150397.470027529 201142.865485638,\
 150403.464011535 201135.266637631,\
 150407.825739533 201127.481037624,\
 150414.301515542 201109.016653612,\
 150431.792971551 201057.519821577,\
 150442.85677956 201026.858701557,\
 150454.530123569 200999.312717538,\
 150472.404939577 200955.342029508,\
 150483.516619585 200927.052237488,\
 150500.807755597 200883.890765458,\
 150516.94650761 200844.146253429,\
 150543.214411631 200773.35943738,\
 150546.079307631 200764.489805374,\
 150548.592075631 200754.511565369)"""
        assert int(w.status_id) == 4
        assert isinstance(w.status, Statuswegsegment)
        assert int(w._methode_id) == 3
        assert isinstance(w.methode, Geometriemethodewegsegment)
        assert isinstance(w.metadata, Metadata)
        assert w.metadata.begin_datum == '1830-01-01 00:00:00'
        assert w.metadata.begin_tijd == '2013-04-12 20:12:12.687000'
        assert isinstance(w.metadata.begin_bewerking, Bewerking)
        assert int(w.metadata.begin_bewerking.id) == 3
        assert isinstance(w.metadata.begin_organisatie, Organisatie)
        assert int(w.metadata.begin_organisatie.id) == 1
        assert 'Wegsegment 108724' == str(w)
        assert 'Wegsegment(108724)' == repr(w)

    def test_check_gateway_not_set(self):
        w = Wegsegment(1, 4)
        with pytest.raises(RuntimeError):
            w.check_gateway()

    def test_status(self, crab_gateway, crab_service):
        crab_service.ListStatusWegsegmenten.return_value = Mock(
            CodeItem=[Mock(Code=4)]
        )
        w = Wegsegment('108724', 4)
        w.set_gateway(crab_gateway)
        status = w.status
        assert isinstance(status, Statuswegsegment)

    def test_methode(self, crab_gateway, crab_service):
        crab_service.ListGeometriemethodeWegsegmenten.return_value = Mock(
            CodeItem=[Mock(Code=2)]
        )
        crab_service.GetWegsegmentByIdentificatorWegsegment.return_value = (
            Mock(IdentificatorWegsegment='108724', BeginBewerking=1,
                 BeginOrganisatie=1, GeometriemethodeWegsegment=2)
        )
        w = Wegsegment('108724', 4)
        w.set_gateway(crab_gateway)
        methode = w.methode
        assert isinstance(methode, Geometriemethodewegsegment)

    def test_lazy_load(self, crab_gateway, crab_service):
        crab_service.GetWegsegmentByIdentificatorWegsegment.return_value = (
            Mock(IdentificatorWegsegment='108724', BeginBewerking=1,
                 BeginOrganisatie=1, GeometriemethodeWegsegment=3,
                 Geometrie='LINESTRING (150339.255243488 201166.401677653,'
                           '150342.836939491 201165.832525652,'
                           '150345.139531493 201165.466573652,'
                           '150349.791371495 201164.769421652)'
                 )
        )
        crab_service.ListGeometriemethodeWegsegmenten.return_value = Mock(
            CodeItem=[Mock(Code=3)]
        )
        crab_service.ListStatusWegsegmenten.return_value = Mock(
            CodeItem=[Mock(Code=4)]
        )
        w = Wegsegment('108724', 4)
        w.set_gateway(crab_gateway)
        assert w.id == "108724"
        assert int(w.status.id) == 4
        assert int(w.methode.id) == 3
        assert w.geometrie == ('LINESTRING (150339.255243488 201166.401677653,'
                               '150342.836939491 201165.832525652,'
                               '150345.139531493 201165.466573652,'
                               '150349.791371495 201164.769421652)')

        w.metadata.set_gateway(crab_gateway)
        assert isinstance(w.metadata, Metadata)
        assert not w.metadata.begin_datum == None
        assert not w.metadata.begin_tijd == None
        assert isinstance(w.metadata.begin_bewerking, Bewerking)
        assert int(w.metadata.begin_bewerking.id) == 1
        assert isinstance(w.metadata.begin_organisatie, Organisatie)
        assert int(w.metadata.begin_organisatie.id) == 1


class TestTerreinobject:
    def test_fully_initialised(self):
        t = Terreinobject(
            "13040_C_1747_G_002_00",
            Aardterreinobject(
                1,
                'kadPerceel',
                'Perceel volgens het Kadaster.'
            ),
            (190708.59, 224667.59),
            (190700.24, 224649.87, 190716.95, 224701.7),
            Metadata(
                '1998-01-01 00:00:00',
                '2009-09-11 12:46:55.693000',
                Bewerking(3, '', ''),
                Organisatie(3, '', '')
            )
        )
        assert t.id == "13040_C_1747_G_002_00"
        assert t.centroid == (190708.59, 224667.59)
        assert t.bounding_box == (190700.24, 224649.87, 190716.95, 224701.7)
        assert int(t.aard_id) == 1
        assert isinstance(t.aard, Aardterreinobject)
        assert isinstance(t.metadata, Metadata)
        assert t.metadata.begin_datum == '1998-01-01 00:00:00'
        assert t.metadata.begin_tijd == '2009-09-11 12:46:55.693000'
        assert isinstance(t.metadata.begin_bewerking, Bewerking)
        assert int(t.metadata.begin_bewerking.id) == 3
        assert isinstance(t.metadata.begin_organisatie, Organisatie)
        assert int(t.metadata.begin_organisatie.id) == 3
        assert 'Terreinobject 13040_C_1747_G_002_00' == str(t)
        assert 'Terreinobject(13040_C_1747_G_002_00)' == repr(t)

    def test_lazy_load(self, crab_gateway, crab_service):
        crab_service.GetTerreinobjectByIdentificatorTerreinobject\
            .return_value = Mock(
                IdentificatorTerreinobject='13040_C_1747_G_002_00',
                BeginBewerking=1, BeginOrganisatie=1,
                CenterX=190708.59, CenterY=224667.58,
                MinimumX=190700.24, MinimumY=224649.87, MaximumX=190716.95,
                MaximumY=224701.7
            )
        crab_service.ListAardTerreinobjecten.return_value = Mock(
            CodeItem=[Mock(Code=1)]
        )
        t = Terreinobject("13040_C_1747_G_002_00", 1)
        t.set_gateway(crab_gateway)
        assert t.id == "13040_C_1747_G_002_00"
        assert t.centroid == (190708.59, 224667.58)
        assert t.bounding_box == (190700.24, 224649.87, 190716.95, 224701.7)
        assert int(t.aard.id) == 1
        t.metadata.set_gateway(crab_gateway)
        assert isinstance(t.metadata, Metadata)
        assert not t.metadata.begin_datum == None
        assert not t.metadata.begin_tijd == None
        assert isinstance(t.metadata.begin_bewerking, Bewerking)
        assert int(t.metadata.begin_bewerking.id) == 1
        assert isinstance(t.metadata.begin_organisatie, Organisatie)
        assert int(t.metadata.begin_organisatie.id) == 1

    def test_aard(self, crab_gateway, crab_service):
        crab_service.ListAardTerreinobjecten.return_value = Mock(
            CodeItem=[Mock(Code=1)]
        )
        t = Terreinobject("13040_C_1747_G_002_00", 1)
        t.set_gateway(crab_gateway)
        assert isinstance(t.aard, Aardterreinobject)


class TestPerceel:
    def test_fully_initialised(self):
        p = Perceel(
            "13040C1747/00G002",
            (190708.59, 224667.59),
            Metadata(
                '1998-01-01 00:00:00',
                '2009-09-11 12:46:55.693000',
                Bewerking(3, '', ''),
                Organisatie(3, '', '')
            )
        )
        assert p.id == "13040C1747/00G002"
        assert p.centroid == (190708.59, 224667.59)
        assert isinstance(p.metadata, Metadata)
        assert p.metadata.begin_datum == '1998-01-01 00:00:00'
        assert p.metadata.begin_tijd == '2009-09-11 12:46:55.693000'
        assert isinstance(p.metadata.begin_bewerking, Bewerking)
        assert int(p.metadata.begin_bewerking.id) == 3
        assert isinstance(p.metadata.begin_organisatie, Organisatie)
        assert int(p.metadata.begin_organisatie.id) == 3
        assert 'Perceel 13040C1747/00G002' == str(p)
        assert 'Perceel(13040C1747/00G002)' == repr(p)

    def test_lazy_load(self, crab_gateway, crab_service):
        crab_service.GetPerceelByIdentificatorPerceel.return_value = Mock(
            IdentificatorPerceel='13040C1747/00G002',
            BeginBewerking=1, BeginOrganisatie=1, CenterX=190708.59,
            CenterY=224667.58,
        )
        p = Perceel("13040C1747/00G002")
        p.set_gateway(crab_gateway)
        assert p.id == "13040C1747/00G002"
        assert p.centroid == (190708.59, 224667.58)
        p.metadata.set_gateway(crab_gateway)
        assert isinstance(p.metadata, Metadata)
        assert p.metadata.begin_datum is not None
        assert p.metadata.begin_tijd is not None
        assert isinstance(p.metadata.begin_bewerking, Bewerking)
        assert int(p.metadata.begin_bewerking.id) == 1
        assert isinstance(p.metadata.begin_organisatie, Organisatie)
        assert int(p.metadata.begin_organisatie.id) == 1

    def test_huisnummers(self, crab_gateway, crab_service):
        crab_service.GetPerceelByIdentificatorPerceel.return_value = Mock(
            IdentificatorPerceel='13040C1747/00G002',
            BeginBewerking=1, BeginOrganisatie=1
        )
        crab_service.ListHuisnummersWithStatusByIdentificatorPerceel\
            .return_value = Mock(
                HuisnummerWithStatusItem=[Mock(HuisnummerId=1)]
            )
        crab_service.GetHuisnummerWithStatusByHuisnummerId.return_value = (
            Mock(HuisnummerId=1, BeginBewerking=1, BeginOrganisatie=1)
        )
        p = crab_gateway.get_perceel_by_id('13040C1747/00G002')
        hnrs = p.huisnummers
        assert isinstance(hnrs, list)
        assert [h.id for h in hnrs] == [h.id for h in crab_gateway.list_huisnummers_by_perceel('13040C1747/00G002')]

    def test_postadressen(self, crab_gateway, crab_service):
        crab_service.GetPerceelByIdentificatorPerceel.return_value = Mock(
            IdentificatorPerceel='13040C1747/00G002',
            BeginBewerking=1, BeginOrganisatie=1
        )
        crab_service.ListHuisnummersWithStatusByIdentificatorPerceel\
            .return_value = Mock(
                HuisnummerWithStatusItem=[Mock(HuisnummerId=1)]
            )
        crab_service.GetHuisnummerWithStatusByHuisnummerId.return_value = (
            Mock(HuisnummerId=1, BeginBewerking=1, BeginOrganisatie=1,
                 StatusHuisnummer=3)
        )
        crab_service.ListStatusHuisnummers.return_value = Mock(
            CodeItem=[Mock(Code='3')]
        )
        crab_service.GetPostadresByHuisnummerId.return_value = Mock(
            Postadres='Steenweg op Oosthoven 51, 2300 Turnhout'
        )
        p = crab_gateway.get_perceel_by_id('13040C1747/00G002')
        postadressen = p.postadressen
        assert isinstance(postadressen, list)
        assert ['Steenweg op Oosthoven 51, 2300 Turnhout'] == postadressen


class TestGebouw:
    def test_fully_initialised(self):
        g = Gebouw(
            "1538575",
            Aardgebouw(1, 'hoofdgebouw', 'hoofdgebouw volgens het GRB'),
            Statusgebouw(4, 'inGebruik', None),
            Geometriemethodegebouw(3, 'grb', None),
            """POLYGON ((190712.36432739347 224668.5216938965,\
 190706.26007138938 224667.54428589717,\
 190706.03594338894 224668.89276589826,\
 190704.89699938893 224668.66159789637,\
 190705.350887388 224666.14575789496,\
 190708.31754338741 224649.70287788659,\
 190717.16349539906 224653.81065388769,\
 190713.40490339696 224663.38582189381,\
 190712.36432739347 224668.5216938965))""",
            Metadata(
                '1830-01-01 00:00:00',
                '2011-05-19 10:51:09.483000',
                Bewerking(1, '', ''),
                Organisatie(5, '', '')
            )
        )
        assert g.id, 1538575
        assert int(g.aard_id) == 1
        assert isinstance(g.aard, Aardgebouw)
        assert int(g.status_id) == 4
        assert isinstance(g.status, Statusgebouw)
        assert int(g._methode_id) == 3
        assert isinstance(g.methode, Geometriemethodegebouw)
        assert g.geometrie == """POLYGON ((190712.36432739347 224668.5216938965,\
 190706.26007138938 224667.54428589717,\
 190706.03594338894 224668.89276589826,\
 190704.89699938893 224668.66159789637,\
 190705.350887388 224666.14575789496,\
 190708.31754338741 224649.70287788659,\
 190717.16349539906 224653.81065388769,\
 190713.40490339696 224663.38582189381,\
 190712.36432739347 224668.5216938965))"""
        assert isinstance(g.metadata, Metadata)
        assert g.metadata.begin_datum == '1830-01-01 00:00:00'
        assert g.metadata.begin_tijd == '2011-05-19 10:51:09.483000'
        assert isinstance(g.metadata.begin_bewerking, Bewerking)
        assert int(g.metadata.begin_bewerking.id) == 1
        assert isinstance(g.metadata.begin_organisatie, Organisatie)
        assert int(g.metadata.begin_organisatie.id) == 5
        assert 'Gebouw 1538575' == str(g)
        assert 'Gebouw(1538575)' == repr(g)

    def test_lazy_load(self, crab_gateway, crab_service):
        crab_service.ListAardGebouwen.return_value = Mock(
            CodeItem=[Mock(Code=1)]
        )
        crab_service.ListStatusGebouwen.return_value = Mock(
            CodeItem=[Mock(Code=4)]
        )
        crab_service.ListGeometriemethodeGebouwen.return_value = Mock(
            CodeItem=[Mock(Code=3)]
        )
        crab_service.GetGebouwByIdentificatorGebouw.return_value = Mock(
            IdentificatorGebouw=1538575, BeginBewerking=1, BeginOrganisatie=1,
            GeometriemethodeGebouw=3,
            Geometrie="POLYGON ((190712.36432739347 224668.5216938965,"
                      "190706.26007138938 224667.54428589717,"
                      "190712.36432739347 224668.5216938965))"
        )
        g = Gebouw("1538575", 1, 4)
        g.set_gateway(crab_gateway)
        assert g.id == 1538575
        assert int(g.aard.id) == 1
        assert int(g.status.id) == 4
        assert int(g.methode.id) == 3
        assert g.geometrie == (
            "POLYGON ((190712.36432739347 224668.5216938965,"
            "190706.26007138938 224667.54428589717,"
            "190712.36432739347 224668.5216938965))"
        )
        g.metadata.set_gateway(crab_gateway)
        assert isinstance(g.metadata, Metadata)
        assert g.metadata.begin_datum is not None
        assert g.metadata.begin_tijd is not None
        assert isinstance(g.metadata.begin_bewerking, Bewerking)
        assert int(g.metadata.begin_bewerking.id) == 1
        assert isinstance(g.metadata.begin_organisatie, Organisatie)
        assert int(g.metadata.begin_organisatie.id) == 1

    def test_aard(self, crab_gateway, crab_service):
        crab_service.ListAardGebouwen.return_value = Mock(
            CodeItem=[Mock(Code=1)]
        )
        g = Gebouw("1538575", 1, 4)
        g.set_gateway(crab_gateway)
        aard = g.aard
        assert isinstance(aard, Aardgebouw)

    def test_status(self, crab_gateway, crab_service):
        crab_service.ListStatusGebouwen.return_value = Mock(
            CodeItem=[Mock(Code=4)]
        )
        g = Gebouw("1538575", 1, 4)
        g.set_gateway(crab_gateway)
        status = g.status
        assert isinstance(status, Statusgebouw)

    def test_methode(self, crab_gateway, crab_service):
        crab_service.ListGeometriemethodeGebouwen.return_value = Mock(
            CodeItem=[Mock(Code=3)]
        )
        crab_service.GetGebouwByIdentificatorGebouw.return_value = Mock(
            IdentificatorGebouw=1538575, BeginBewerking=1, BeginOrganisatie=1,
            GeometriemethodeGebouw=3
        )
        g = Gebouw("1538575", 1, 4)
        g.set_gateway(crab_gateway)
        methode = g.methode
        assert isinstance(methode, Geometriemethodegebouw)


class TestMetadata:
    def test_fully_initialised(self):
        m = Metadata(
            '1830-01-01 00:00:00',
            '2003-12-06 21:42:11.117000',
            Bewerking(1, '', ''),
            Organisatie(6, '', '')
        )
        assert m.begin_datum == '1830-01-01 00:00:00'
        assert m.begin_tijd == '2003-12-06 21:42:11.117000'
        assert isinstance(m.begin_bewerking, Bewerking)
        assert int(m.begin_bewerking.id) == 1
        assert isinstance(m.begin_organisatie, Organisatie)
        assert int(m.begin_organisatie.id) == 6
        assert 'Begin datum: 1830-01-01 00:00:00' == str(m)

    def test_lazy_load(self, crab_gateway, crab_service):
        m = Metadata(
            '1830-01-01 00:00:00',
            '2003-12-06 21:42:11.117000',
            1,
            1,
            gateway=crab_gateway
        )
        assert m.begin_datum == '1830-01-01 00:00:00'
        assert m.begin_tijd == '2003-12-06 21:42:11.117000'
        assert isinstance(m.begin_bewerking, Bewerking)
        assert int(m.begin_bewerking.id) == 1
        assert isinstance(m.begin_organisatie, Organisatie)
        assert int(m.begin_organisatie.id) == 1


class TestSubadres:
    def test_fully_initialised(self):
        s = Subadres(
            1120936,
            "B",
            Statussubadres(3, 'inGebruik', 'None'),
            38020,
            Aardsubadres(1, 'gemeente', 'Gemeente.'),
            Metadata(
                '1830-01-01 00:00:00',
                '2011-04-29 13:27:40.230000',
                Bewerking(1, '', ''),
                Organisatie(5, '', '')
            )
        )
        assert s.id == 1120936
        assert s.subadres == "B"
        assert int(s.status_id) == 3
        assert isinstance(s.status, Statussubadres)
        assert int(s.huisnummer_id) == 38020
        assert isinstance(s.metadata, Metadata)
        assert s.metadata.begin_datum == '1830-01-01 00:00:00'
        assert s.metadata.begin_tijd, '2011-04-29 13:27:40.230000'
        assert isinstance(s.metadata.begin_bewerking, Bewerking)
        assert int(s.metadata.begin_bewerking.id) == 1
        assert isinstance(s.metadata.begin_organisatie, Organisatie)
        assert int(s.metadata.begin_organisatie.id) == 5
        assert 'B (1120936)' == str(s)
        assert "Subadres(1120936, 3, 'B', 38020)" == repr(s)

    def test_str_dont_lazy_load(self):
        s = Subadres(1120936, 'B', 3)
        assert 'B (1120936)' == str(s)

    def test_lazy_load(self, crab_gateway, crab_service):
        crab_service.ListStatusHuisnummers.return_value = Mock(
            CodeItem=[Mock(Code=3)]
        )
        crab_service.GetHuisnummerWithStatusByHuisnummerId.return_value = Mock(
            HuisnummerId=38020, BeginBewerking=1, BeginOrganisatie=1
        )
        crab_service.GetSubadresWithStatusBySubadresId.return_value = Mock(
            SubadresId=1120936, BeginBewerking=1, BeginOrganisatie=1,
            AardSubadres=2
        )
        crab_service.ListAardSubadressen.return_value = Mock(
            CodeItem=[Mock(Code=2)]
        )
        s = Subadres(1120936, 'B', 3)
        s.set_gateway(crab_gateway)
        assert s.id == 1120936
        assert int(s.status.id) == 3
        assert s.subadres == "B"
        assert isinstance(s.aard, Aardsubadres)
        assert int(s.huisnummer.id) == 38020
        s.metadata.set_gateway(crab_gateway)
        assert isinstance(s.metadata, Metadata)
        assert s.metadata.begin_datum is not None
        assert s.metadata.begin_tijd is not None
        assert isinstance(s.metadata.begin_bewerking, Bewerking)
        assert int(s.metadata.begin_bewerking.id) == 1
        assert isinstance(s.metadata.begin_organisatie, Organisatie)
        assert int(s.metadata.begin_organisatie.id) == 1

    def test_check_gateway_not_set(self):
        s = Subadres(1, 3, 'B', 129462)
        with pytest.raises(RuntimeError):
            s.check_gateway()

    def test_adresposities(self, crab_gateway, crab_service):
        crab_service.ListAdrespositiesBySubadresId.return_value = Mock(
            AdrespositieItem=[Mock()]
        )
        s = Subadres(1120936, 'B', 3)
        s.set_gateway(crab_gateway)
        adresposities = s.adresposities
        assert isinstance(adresposities, list)

    def test_postadres(self, crab_gateway, crab_service):
        crab_service.GetPostadresBySubadresId.return_value = Mock(
            Postadres='Antoon van Brabantstraat 7 bus B, 2630 Aartselaar'
        )
        s = Subadres(1120936, 'B', 3)
        s.set_gateway(crab_gateway)
        assert s.postadres == 'Antoon van Brabantstraat 7 bus B, 2630 Aartselaar'


class TestAdrespositie:
    def test_fully_initialised(self):
        a = Adrespositie(
            4087928,
            Herkomstadrespositie(
                '6',
                'manueleAanduidingVanToegangTotDeWeg',
                None
            ),
            """POINT(190705.34 224675.26)""",
            Aardadres(
                '1',
                'subAdres',
                'Aanduiding van een plaats op een huisnummer'
            ),
            Metadata(
                '1830-01-01 00:00:00',
                '',
                None,
                None
            )
        )
        assert a.id == 4087928
        assert str(a.herkomst.id) == '6'
        assert a.geometrie == 'POINT(190705.34 224675.26)'
        assert str(a.aard.id) == '1'
        assert isinstance(a.metadata, Metadata)
        assert a.metadata.begin_datum == '1830-01-01 00:00:00'
        assert 'Adrespositie 4087928' == str(a)
        assert "Adrespositie(4087928, 6)" == repr(a)

    def test_str_dont_lazy_load(self, crab_gateway):
        a = Adrespositie(4087928, 2)
        a.set_gateway(crab_gateway)
        assert 'Adrespositie 4087928' == str(a)

    def test_lazy_load(self, crab_gateway, crab_service):
        crab_service.GetAdrespositieByAdrespositieId.return_value = Mock(
            AdrespositieId=4428005, BeginBewerking=1, BeginOrganisatie=1,
            Geometrie='POINT (74414.91 225777.36)', AardAdres=2,
            BeginDatum='1830-01-01 00:00:00'
        )
        crab_service.ListAardAdressen.return_value = Mock(
            CodeItem=[Mock(Code=2)]
        )
        a = Adrespositie(4428005, 3)
        a.set_gateway(crab_gateway)
        assert a.id == 4428005
        assert a.herkomst_id == 3
        assert str(a.geometrie) == 'POINT (74414.91 225777.36)'
        assert int(a.aard.id) == 2
        assert isinstance(a.metadata, Metadata)
        assert a.metadata.begin_datum == '1830-01-01 00:00:00'

    def test_check_gateway_not_set(self):
        a = Adrespositie(4087928, 2)
        with pytest.raises(RuntimeError):
            a.check_gateway()
