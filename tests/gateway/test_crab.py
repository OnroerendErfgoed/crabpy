# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import six

import pytest

from crabpy.client import (
    crab_factory
)

from crabpy.gateway.exception import (
    GatewayRuntimeException,
    GatewayResourceNotFoundException
)

from crabpy.gateway.crab import (
    CrabGateway, Gewest,
    Gemeente, Taal,
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
    Gebouw, Metadata, Provincie, Subadres,
    Adrespositie
)

@pytest.mark.skipif(
    not pytest.config.getoption('--crab-integration'),
    reason='No CRAB Integration tests required'
)
class TestCrabGateway:

    def setup_method(self, method):
        self.crab_client = crab_factory()
        self.crab = CrabGateway(
            self.crab_client
        )

    def teardown_method(self, method):
        self.crab_client = None
        self.crab = None

    def test_list_gewesten(self):
        res = self.crab.list_gewesten()
        assert isinstance(res, list)
        assert isinstance(res[0], Gewest)

    def test_get_gewest_by_id(self):
        res = self.crab.get_gewest_by_id(2)
        assert isinstance(res, Gewest)
        assert res.id == 2
        assert isinstance(res.centroid, tuple)
        assert isinstance(res.bounding_box, tuple)

    def test_get_gewest_by_unexisting_id(self):
        with pytest.raises(GatewayResourceNotFoundException):
            self.crab.get_gewest_by_id(-1)

    def test_list_gemeenten_default(self):
        res = self.crab.list_gemeenten()
        assert isinstance(res, list)
        assert isinstance(res[0], Gemeente)
        assert res[0].gewest.id == 2

    def test_list_gemeenten_Vlaanderen(self):
        gewest = Gewest(2)
        res = self.crab.list_gemeenten(gewest)
        assert isinstance(res, list)
        assert isinstance(res[0], Gemeente)
        assert res[0].gewest.id == 2

    def test_list_provincies(self):
        gewest = Gewest(1)
        res = self.crab.list_provincies(gewest)
        assert isinstance(res, list)
        gewest = Gewest(3)
        res = self.crab.list_provincies(gewest)
        assert isinstance(res, list)
        gewest = Gewest(2)
        res = self.crab.list_provincies(gewest)
        assert isinstance(res, list)
        assert isinstance(res[0], Provincie)
        assert res[0].gewest.id == 2
        gewest = 2
        res = self.crab.list_provincies(gewest)
        assert isinstance(res, list)
        assert isinstance(res[0], Provincie)
        assert res[0].gewest.id == 2

    def test_get_provincie_by_id(self):
        res = self.crab.get_provincie_by_id(10000)
        assert isinstance(res, Provincie)
        assert res.niscode == 10000
        res = self.crab.get_provincie_by_id(20001)
        assert isinstance(res, Provincie)
        assert res.niscode == 20001
        res = self.crab.get_provincie_by_id(20002)
        assert isinstance(res, Provincie)
        assert res.niscode == 20002
        res = self.crab.get_provincie_by_id(30000)
        assert isinstance(res, Provincie)
        assert res.niscode == 30000
        res = self.crab.get_provincie_by_id(40000)
        assert isinstance(res, Provincie)
        assert res.niscode == 40000
        res = self.crab.get_provincie_by_id(50000)
        assert isinstance(res, Provincie)
        assert (res.niscode, 50000)
        res = self.crab.get_provincie_by_id(60000)
        assert isinstance(res, Provincie)
        assert (res.niscode, 60000)
        res = self.crab.get_provincie_by_id(70000)
        assert isinstance(res, Provincie)
        assert (res.niscode, 70000)
        res = self.crab.get_provincie_by_id(80000)
        assert isinstance(res, Provincie)
        assert (res.niscode, 80000)
        res = self.crab.get_provincie_by_id(90000)
        assert isinstance(res, Provincie)
        assert (res.niscode, 90000)

    def test_get_provincie_by_unexisting_id(self):
        with pytest.raises(GatewayResourceNotFoundException):
            self.crab.get_provincie_by_id(-1)

    def test_list_gemeenten_by_provincie(self):
        provincie = Provincie(10000, 'Antwerpen', Gewest(2))
        res = self.crab.list_gemeenten_by_provincie(provincie)
        assert isinstance(res, list)
        assert isinstance(res[0], Gemeente)
        assert (str(res[0].niscode)[0], '1')
        provincie = 10000
        res = self.crab.list_gemeenten_by_provincie(provincie)
        assert isinstance(res, list)
        assert isinstance(res[0], Gemeente)
        assert (str(res[0].niscode)[0], '1')

    def test_get_gemeente_by_id(self):
        res = self.crab.get_gemeente_by_id(1)
        assert isinstance(res, Gemeente)
        assert (res.id, 1)
        with pytest.raises(GatewayRuntimeException):
            self.crab.get_gemeente_by_id('gent')

    def test_get_gemeente_by_niscode(self):
        res = self.crab.get_gemeente_by_niscode(11001)
        assert isinstance(res, Gemeente)
        assert (res.niscode, 11001)
        
    def test_get_gemeente_by_unexisting_niscode(self):
        with pytest.raises(GatewayResourceNotFoundException):
            self.crab.get_gemeente_by_niscode(-1)

    def test_list_talen(self):
        res = self.crab.list_talen()
        assert isinstance(res, list)
        assert isinstance(res[0], Taal)

    def test_list_bewerkingen(self):
        res = self.crab.list_bewerkingen()
        assert isinstance(res, list)
        assert isinstance(res[0], Bewerking)

    def test_list_organisaties(self):
        res = self.crab.list_organisaties()
        assert isinstance(res, list)
        assert isinstance(res[0], Organisatie)

    def test_list_aardsubadressen(self):
        res = self.crab.list_aardsubadressen()
        assert isinstance(res, list)
        assert isinstance(res[0], Aardsubadres)

    def test_list_aardadressen(self):
        res = self.crab.list_aardadressen()
        assert isinstance(res, list)
        assert isinstance(res[0], Aardadres)

    def test_list_aardgebouwen(self):
        res = self.crab.list_aardgebouwen()
        assert isinstance(res, list)
        assert isinstance(res[0], Aardgebouw)

    def test_list_aarwegobjecten(self):
        res = self.crab.list_aardwegobjecten()
        assert isinstance(res, list)
        assert isinstance(res[0], Aardwegobject)

    def test_list_aardterreinobjecten(self):
        res = self.crab.list_aardterreinobjecten()
        assert isinstance(res, list)
        assert isinstance(res[0], Aardterreinobject)

    def test_list_statushuisnummers(self):
        res = self.crab.list_statushuisnummers()
        assert isinstance(res, list)
        assert isinstance(res[0], Statushuisnummer)

    def test_list_statussubadressen(self):
        res = self.crab.list_statussubadressen()
        assert isinstance(res, list)
        assert isinstance(res[0], Statussubadres)

    def test_list_statusstraatnamen(self):
        res = self.crab.list_statusstraatnamen()
        assert isinstance(res, list)
        assert isinstance(res[0], Statusstraatnaam)

    def test_list_statuswegsegmenten(self):
        res = self.crab.list_statuswegsegmenten()
        assert isinstance(res, list)
        assert isinstance(res[0], Statuswegsegment)

    def test_list_geometriemethodewegsegmenten(self):
        res = self.crab.list_geometriemethodewegsegmenten()
        assert isinstance(res, list)
        assert isinstance(res[0], Geometriemethodewegsegment)

    def test_list_statusgebouwen(self):
        res = self.crab.list_statusgebouwen()
        assert isinstance(res, list)
        assert isinstance(res[0], Statusgebouw)

    def test_list_gemetriemethodegebouwen(self):
        res = self.crab.list_geometriemethodegebouwen()
        assert isinstance(res, list)
        assert isinstance(res[0], Geometriemethodegebouw)

    def test_list_herkomstadrespositie(self):
        res = self.crab.list_herkomstadresposities()
        assert isinstance(res, list)
        assert isinstance(res[0], Herkomstadrespositie)

    def test_list_straten(self):
        res = self.crab.list_straten(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Straat)
        gemeente = self.crab.get_gemeente_by_id(1)
        assert isinstance(gemeente, Gemeente)
        res = self.crab.list_straten(gemeente)
        assert isinstance(res, list)
        assert isinstance(res[0], Straat)

    def test_list_straten_empty(self):
        res = self.crab.list_straten(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_straat_by_id(self):
        res = self.crab.get_straat_by_id(1)
        assert isinstance(res, Straat)
        assert res.id == 1
        
    def test_get_straat_by_unexisting_id(self):
        with pytest.raises(GatewayResourceNotFoundException):
            self.crab.get_straat_by_id(-1)

    def test_list_huisnummers_by_straat(self):
        res = self.crab.list_huisnummers_by_straat(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Huisnummer)
        straat = self.crab.get_straat_by_id(1)
        res = self.crab.list_huisnummers_by_straat(straat)
        assert isinstance(res, list)
        assert isinstance(res[0], Huisnummer)

    def test_list_huisnummers_by_straat_empty(self):
        res = self.crab.list_huisnummers_by_straat(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_huisnummer_by_id(self):
        res = self.crab.get_huisnummer_by_id(1)
        assert isinstance(res, Huisnummer)
        assert res.id == 1
    
    def test_get_huisnummer_by_unexisting_id(self):
        with pytest.raises(GatewayResourceNotFoundException):
            self.crab.get_huisnummer_by_id(-1)

    def test_get_huisnummer_by_nummer_and_straat(self):
        res = self.crab.get_huisnummer_by_nummer_and_straat(1, 1)
        assert isinstance(res, Huisnummer)
        assert (res.huisnummer, '1')
        assert (res.straat.id, 1)
        straat = self.crab.get_straat_by_id(1)
        res = self.crab.get_huisnummer_by_nummer_and_straat(1, straat)
        assert isinstance(res, Huisnummer)
        assert res.huisnummer == '1'
        
    def test_get_huisnummer_by_unexisting_nummer_and_straat(self):
        with pytest.raises(GatewayResourceNotFoundException):
            self.crab.get_huisnummer_by_nummer_and_straat(-1, -1)

    def test_list_postkantons_by_gemeente(self):
        res = self.crab.list_postkantons_by_gemeente(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Postkanton)
        gemeente = self.crab.get_gemeente_by_id(1)
        res = self.crab.list_postkantons_by_gemeente(gemeente)
        assert isinstance(res, list)
        assert isinstance(res[0], Postkanton)

    def test_list_postkantons_by_gemeente_empty(self):
        res = self.crab.list_postkantons_by_gemeente(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_postkanton_by_huisnummer(self):
        res = self.crab.get_postkanton_by_huisnummer(1)
        assert isinstance(res, Postkanton)
        huisnummer = self.crab.get_huisnummer_by_id(1)
        res = self.crab.get_postkanton_by_huisnummer(huisnummer)
        assert isinstance(res, Postkanton)
        
    def test_get_postkanton_by_unexisting_huisnummer(self):
        with pytest.raises(GatewayResourceNotFoundException):
            self.crab.get_postkanton_by_huisnummer(-1)

    def test_list_wegobjecten_by_straat(self):
        res = self.crab.list_wegobjecten_by_straat(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Wegobject)
        straat = self.crab.get_straat_by_id(1)
        res = self.crab.list_wegobjecten_by_straat(straat)
        assert isinstance(res, list)
        assert isinstance(res[0], Wegobject)

    def test_list_wegobjecten_by_straat(self):
        res = self.crab.list_wegobjecten_by_straat(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_wegobject_by_id(self):
        res = self.crab.get_wegobject_by_id("53839893")
        assert isinstance(res, Wegobject)
        assert res.id == "53839893"
        
    def test_get_wegobject_by_unexisting_id(self):
        with pytest.raises(GatewayResourceNotFoundException):
            self.crab.get_wegobject_by_id(-1)

    def test_list_wegsegmenten_by_straat(self):
        res = self.crab.list_wegsegmenten_by_straat(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Wegsegment)
        straat = self.crab.get_straat_by_id(1)
        res = self.crab.list_wegsegmenten_by_straat(straat)
        assert isinstance(res, list)
        assert isinstance(res[0], Wegsegment)

    def test_list_wegsegmenten_by_straat_empty(self):
        res = self.crab.list_wegsegmenten_by_straat(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_wegsegment_by_id(self):
        res = self.crab.get_wegsegment_by_id("108724")
        assert isinstance(res, Wegsegment)
        assert res.id == "108724"
    
    def test_get_wegsegment_by_unexisting_id(self):
        with pytest.raises(GatewayResourceNotFoundException):
            self.crab.get_wegsegment_by_id(-1)

    def test_list_terreinobjecten_by_huisnummer(self):
        res = self.crab.list_terreinobjecten_by_huisnummer(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Terreinobject)
        huisnummer = self.crab.get_huisnummer_by_id(1)
        res = self.crab.list_terreinobjecten_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert isinstance(res[0], Terreinobject)

    def test_list_terreinobjecten_by_huisnummer_empty(self):
        res = self.crab.list_terreinobjecten_by_huisnummer(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_terreinobject_by_id(self):
        res = self.crab.get_terreinobject_by_id("13040_C_1747_G_002_00")
        assert isinstance(res, Terreinobject)
        assert res.id == "13040_C_1747_G_002_00"
        
    def test_get_terreinobject_by_unexisting_id(self):
        with pytest.raises(GatewayResourceNotFoundException):
            self.crab.get_terreinobject_by_id(-1)

    def test_list_percelen_by_huisnummer(self):
        res = self.crab.list_percelen_by_huisnummer(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Perceel)
        huisnummer = self.crab.get_huisnummer_by_id(1)
        res = self.crab.list_percelen_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert isinstance(res[0], Perceel)

    def test_list_percelen_by_huisnummer_empty(self):
        res = self.crab.list_percelen_by_huisnummer(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_perceel_by_id(self):
        res = self.crab.get_perceel_by_id("13040C1747/00G002")
        assert isinstance(res, Perceel)
        assert res.id == "13040C1747/00G002"
        
    def test_get_perceel_by_unexisting_id(self):
        with pytest.raises(GatewayResourceNotFoundException):
            self.crab.get_perceel_by_id(-1)

    def test_list_gebouwen_by_huisnummer(self):
        res = self.crab.list_gebouwen_by_huisnummer(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Gebouw)
        huisnummer = self.crab.get_huisnummer_by_id(1)
        res = self.crab.list_gebouwen_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert isinstance(res[0], Gebouw)

    def test_list_gebouwen_by_huisnummer_empty(self):
        res = self.crab.list_gebouwen_by_huisnummer(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_gebouw_by_id(self):
        res = self.crab.get_gebouw_by_id("1538575")
        assert isinstance(res, Gebouw)
        assert res.id == 1538575
        
    def test_get_gebouw_by_unexisting_id(self):
        with pytest.raises(GatewayResourceNotFoundException):
            self.crab.get_gebouw_by_id(-1)

    def test_list_subadressen_by_huisnummer(self):
        res = self.crab.list_subadressen_by_huisnummer(129462)
        assert isinstance(res, list)
        assert isinstance(res[0], Subadres)
        huisnummer = self.crab.get_huisnummer_by_id(129462)
        res = self.crab.list_subadressen_by_huisnummer(huisnummer)
        assert isinstance(res, list)
        assert isinstance(res[0], Subadres)

    def test_list_subadressen_by_huisnummer_empty(self):
        res = self.crab.list_subadressen_by_huisnummer(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_subadres_by_id(self):
        res = self.crab.get_subadres_by_id(1120936)
        assert isinstance(res, Subadres)
        assert res.id == 1120936
        
    def test_get_subadres_by_unexisting_id(self):
        with pytest.raises(GatewayResourceNotFoundException):
            self.crab.get_subadres_by_id(-1)

    def test_list_adresposities_by_huisnummer(self):
        res = self.crab.list_adresposities_by_huisnummer(1)
        assert isinstance(res, list)
        assert isinstance(res[0], Adrespositie)

    def test_list_adresposities_by_huisnummer_empty(self):
        res = self.crab.list_adresposities_by_huisnummer(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_list_adresposities_by_nummer_and_straat(self):
        res = self.crab.list_adresposities_by_nummer_and_straat(1, 1)
        assert isinstance(res, list)
        assert isinstance(res[0], Adrespositie)

    def test_list_adresposities_by_nummer_and_straat_empty(self):
        res = self.crab.list_adresposities_by_nummer_and_straat(0, 0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_list_adresposities_by_subadres(self):
        res = self.crab.list_adresposities_by_subadres(1120936)
        assert isinstance(res, list)
        assert isinstance(res[0], Adrespositie)

    def test_list_adresposities_by_subadres_empty(self):
        res = self.crab.list_adresposities_by_subadres(0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_list_adresposities_by_subadres_and_huisnummer(self):
        res = self.crab.list_adresposities_by_subadres_and_huisnummer('A', 129462)
        assert isinstance(res, list)
        assert isinstance(res[0], Adrespositie)

    def test_list_adresposities_by_subadres_and_huisnummer(self):
        res = self.crab.list_adresposities_by_subadres_and_huisnummer(0, 0)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_get_adrespositie_by_id(self):
        res = self.crab.get_adrespositie_by_id(4087928)
        assert isinstance(res, Adrespositie)
        assert res.id == 4087928
        
    def test_get_adrespositie_by_unexisting_id(self):
        with pytest.raises(GatewayResourceNotFoundException):
            self.crab.get_adrespositie_by_id(-1)


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

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_gemeenten(self):
        crab = CrabGateway(
            crab_factory()
        )
        g = Gewest(2)
        g.set_gateway(crab)
        gemeenten = g.gemeenten
        assert isinstance(gemeenten, list)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_provincies(self):
        crab = CrabGateway(
            crab_factory()
        )
        g = Gewest(2)
        g.set_gateway(crab)
        provincies = g.provincies
        assert isinstance(provincies, list)
        assert len(provincies) == 5

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_lazy_load(self):
        crab = CrabGateway(
            crab_factory()
        )
        g = Gewest(2)
        g.set_gateway(crab)
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

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_gemeenten(self):
        crab = CrabGateway(
            crab_factory()
        )
        p = Provincie(20001, 'Vlaams-Brabant', Gewest(2))
        p.set_gateway(crab)
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
        assert 'Biévène (92)'.encode('utf-8') == str(g)

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

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_lazy_load(self):
        crab = CrabGateway(
            crab_factory()
        )
        g = Gemeente(1, 'Aartselaar', 11001, Gewest(2))
        g.set_gateway(crab)
        assert g.id == 1
        assert g.naam == 'Aartselaar'
        assert g.niscode == 11001
        assert isinstance(g.gewest, Gewest)
        assert int(g.gewest.id) == 2
        assert g.taal.id == 'nl'
        assert g.centroid == (150881.07, 202256.84)
        assert g.bounding_box == (148950.36, 199938.28, 152811.77, 204575.39)
        g.metadata.set_gateway(crab)
        assert isinstance(g.metadata, Metadata)
        assert not g.metadata.begin_datum == None
        assert not g.metadata.begin_tijd == None
        assert isinstance(g.metadata.begin_bewerking, Bewerking)
        assert int(g.metadata.begin_bewerking.id) == 1
        assert isinstance(g.metadata.begin_organisatie, Organisatie)
        assert int(g.metadata.begin_organisatie.id) == 6

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_straten(self):
        crab = CrabGateway(
            crab_factory()
        )
        g = Gemeente(1, 'Aartselaar', 11001, Gewest(3))
        g.set_gateway(crab)
        straten = g.straten
        assert isinstance(straten, list)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_postkantons(self):
        crab = CrabGateway(
            crab_factory()
        )
        g = Gemeente(1, 'Aartselaar', 11001, Gewest(3))
        g.set_gateway(crab)
        postkanton = g.postkantons
        assert isinstance(postkanton, list)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_provincie(self):
        crab = CrabGateway(
            crab_factory()
        )
        g = Gemeente(1, 'Aartselaar', 11001, Gewest(2))
        g.set_gateway(crab)
        provincie = g.provincie
        assert isinstance(provincie, Provincie)
        assert 10000 == provincie.id


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

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_lazy_load(self):
        crab = CrabGateway(
            crab_factory()
        )
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab)
        assert s.id == 1
        assert s.label == 'Acacialaan'
        assert int(s.status.id) == 3
        assert s.namen == (('Acacialaan', 'nl'), (None, None))
        assert int(s.gemeente.id) == 1
        s.metadata.set_gateway(crab)
        assert isinstance(s.metadata, Metadata)
        assert not s.metadata.begin_datum == None
        assert not s.metadata.begin_tijd == None
        assert isinstance(s.metadata.begin_bewerking, Bewerking)
        assert int(s.metadata.begin_bewerking.id) == 3
        assert isinstance(s.metadata.begin_organisatie, Organisatie)
        assert int(s.metadata.begin_organisatie.id) == 1

    def test_str_and_repr_dont_lazy_load(self):
        s = Straat(1, 'Acacialaan', 1, 3)
        assert ('Acacialaan (1)', str(s))
        assert ("Straat(1, 'Acacialaan', 1, 3)", repr(s))

    def test_check_gateway_not_set(self):
        s = Straat(1, 'Acacialaan', 1, 3)
        with pytest.raises(RuntimeError):
            s.check_gateway()

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_huisnummers(self):
        crab = CrabGateway(
            crab_factory()
        )
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab)
        huisnummers = s.huisnummers
        assert isinstance(huisnummers, list)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_taal(self):
        crab = CrabGateway(
            crab_factory()
        )
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab)
        taal = s.taal
        assert isinstance(taal, Taal)
        assert s.taal.id == 'nl'

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_gemeente(self):
        crab = CrabGateway(
            crab_factory()
        )
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab)
        gemeente = s.gemeente
        assert isinstance(gemeente, Gemeente)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_status(self):
        crab = CrabGateway(
            crab_factory()
        )
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab)
        status = s.status
        assert isinstance(status, Statusstraatnaam)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_wegobjecten(self):
        crab = CrabGateway(
            crab_factory()
        )
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab)
        wegobjecten = s.wegobjecten
        assert isinstance(wegobjecten, list)
        assert isinstance(wegobjecten[0], Wegobject)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_wegsegmenten(self):
        crab = CrabGateway(
            crab_factory()
        )
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab)
        wegsegmenten = s.wegsegmenten
        assert isinstance(wegsegmenten, list)
        assert isinstance(wegsegmenten[0], Wegsegment)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_bounding_box(self):
        crab = CrabGateway(crab_factory())
        s = Straat(1, 'Acacialaan', 1, 3)
        s.set_gateway(crab)
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

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_lazy_load(self):
        crab = CrabGateway(
            crab_factory()
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab)
        assert h.id == 1
        assert int(h.status.id) == 3
        assert h.huisnummer == "51"
        assert int(h.straat.id) == 17718
        h.metadata.set_gateway(crab)
        assert isinstance(h.metadata, Metadata)
        assert not h.metadata.begin_datum == None
        assert not h.metadata.begin_tijd == None
        assert isinstance(h.metadata.begin_bewerking, Bewerking)
        assert int(h.metadata.begin_bewerking.id) == 3
        assert isinstance(h.metadata.begin_organisatie, Organisatie)
        assert int(h.metadata.begin_organisatie.id) == 1

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_postkanton(self):
        crab = CrabGateway(
            crab_factory()
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab)
        postkanton = h.postkanton
        assert isinstance(postkanton, Postkanton)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_terreinobjecten(self):
        crab = CrabGateway(
            crab_factory()
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab)
        terreinobjecten = h.terreinobjecten
        assert isinstance(terreinobjecten, list)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_percelen(self):
        crab = CrabGateway(
            crab_factory()
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab)
        percelen = h.percelen
        assert isinstance(percelen, list)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_gebouwen(self):
        crab = CrabGateway(
            crab_factory()
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab)
        gebouwen = h.gebouwen
        assert isinstance(gebouwen, list)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_subadressen(self):
        crab = CrabGateway(
            crab_factory()
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab)
        subadressen = h.subadressen
        assert isinstance(subadressen, list)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_adresposities(self):
        crab = CrabGateway(
            crab_factory()
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab)
        adresposities = h.adresposities
        assert isinstance(adresposities, list)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_status(self):
        crab = CrabGateway(
            crab_factory()
        )
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab)
        status = h.status
        assert isinstance(status, Statushuisnummer)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_bounding_box(self):
        crab = CrabGateway(crab_factory())
        h = Huisnummer(1, 3, '51', 17718)
        h.set_gateway(crab)
        bounding = h.bounding_box
        assert isinstance(bounding, list)
        assert (len(bounding), 4)

    def test_check_gateway_not_set(self):
        h = Huisnummer(1, 3, '51', 17718)
        with pytest.raises(RuntimeError):
            h.check_gateway()


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

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_aard(self):
        crab = CrabGateway(
            crab_factory()
        )
        w = Wegobject("53839893", 4)
        w.set_gateway(crab)
        aard = w.aard
        assert isinstance(aard, Aardwegobject)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_lazy_load(self):
        crab = CrabGateway(
            crab_factory()
        )
        w = Wegobject("53839893", 4)
        w.set_gateway(crab)
        assert w.id == "53839893"
        assert int(w.aard.id) == 4
        assert w.centroid == (150753.46, 200148.41)
        assert w.bounding_box == (150693.58, 200080.56, 150813.35, 200216.27)
        w.metadata.set_gateway(crab)
        assert isinstance(w.metadata, Metadata)
        assert not w.metadata.begin_datum == None
        assert not w.metadata.begin_tijd == None
        assert isinstance(w.metadata.begin_bewerking, Bewerking)
        assert int(w.metadata.begin_bewerking.id) == 1
        assert isinstance(w.metadata.begin_organisatie, Organisatie)
        assert int(w.metadata.begin_organisatie.id) == 8


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

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_status(self):
        crab = CrabGateway(
            crab_factory()
        )
        w = Wegsegment('108724', 4)
        w.set_gateway(crab)
        status = w.status
        assert isinstance(status, Statuswegsegment)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_methode(self):
        crab = CrabGateway(
            crab_factory()
        )
        w = Wegsegment('108724', 4)
        w.set_gateway(crab)
        methode = w.methode
        assert isinstance(methode, Geometriemethodewegsegment)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_lazy_load(self):
        crab = CrabGateway(
            crab_factory()
        )
        w = Wegsegment('108724', 4)
        w.set_gateway(crab)
        assert (w.id, "108724")
        assert (int(w.status.id), 4)
        assert (int(w.methode.id), 3)
        assert (
            w.geometrie,
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
 150548.592075631 200754.511565369)"""
        )
        w.metadata.set_gateway(crab)
        assert isinstance(w.metadata, Metadata)
        assert not w.metadata.begin_datum == None
        assert not w.metadata.begin_tijd == None
        assert isinstance(w.metadata.begin_bewerking, Bewerking)
        assert int(w.metadata.begin_bewerking.id) == 3
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

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_lazy_load(self):
        crab = CrabGateway(
            crab_factory()
        )
        t = Terreinobject("13040_C_1747_G_002_00", 1)
        t.set_gateway(crab)
        assert t.id == "13040_C_1747_G_002_00"
        assert t.centroid == (190708.59, 224667.59)
        assert t.bounding_box == (190700.24, 224649.87, 190716.95, 224701.7)
        assert int(t.aard.id) == 1
        t.metadata.set_gateway(crab)
        assert isinstance(t.metadata, Metadata)
        assert not t.metadata.begin_datum == None
        assert not t.metadata.begin_tijd == None
        assert isinstance(t.metadata.begin_bewerking, Bewerking)
        assert int(t.metadata.begin_bewerking.id) == 3
        assert isinstance(t.metadata.begin_organisatie, Organisatie)
        assert int(t.metadata.begin_organisatie.id) == 3

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_aard(self):
        crab = CrabGateway(
            crab_factory()
        )
        t = Terreinobject("13040_C_1747_G_002_00", 1)
        t.set_gateway(crab)
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

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_lazy_load(self):
        crab = CrabGateway(
            crab_factory()
        )
        p = Perceel("13040C1747/00G002")
        p.set_gateway(crab)
        assert p.id == "13040C1747/00G002"
        assert p.centroid == (190708.59, 224667.59)
        p.metadata.set_gateway(crab)
        assert isinstance(p.metadata, Metadata)
        assert not p.metadata.begin_datum == None
        assert not p.metadata.begin_tijd == None
        assert isinstance(p.metadata.begin_bewerking, Bewerking)
        assert int(p.metadata.begin_bewerking.id) == 3
        assert isinstance(p.metadata.begin_organisatie, Organisatie)
        assert int(p.metadata.begin_organisatie.id) == 3


class GebouwTest:
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

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_lazy_load(self):
        crab = CrabGateway(
            crab_factory()
        )
        g = Gebouw("1538575", 1, 4)
        g.set_gateway(crab)
        assert g.id == 1538575
        assert int(g.aard.id) == 1
        assert int(g.status.id) == 4
        assert int(g.methode.id) == 3
        assert g.geometrie == """POLYGON ((190712.36432739347 224668.5216938965,\
 190706.26007138938 224667.54428589717,\
 190706.03594338894 224668.89276589826,\
 190704.89699938893 224668.66159789637,\
 190705.350887388 224666.14575789496,\
 190708.31754338741 224649.70287788659,\
 190717.16349539906 224653.81065388769,\
 190713.40490339696 224663.38582189381,\
 190712.36432739347 224668.5216938965))"""
        g.metadata.set_gateway(crab)
        assert isinstance(g.metadata, Metadata)
        assert not g.metadata.begin_datum == None
        assert not g.metadata.begin_tijd == None
        assert isinstance(g.metadata.begin_bewerking, Bewerking)
        assert int(g.metadata.begin_bewerking.id) == 3
        assert isinstance(g.metadata.begin_organisatie, Organisatie)
        assert int(g.metadata.begin_organisatie.id) == 1

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_aard(self):
        crab = CrabGateway(
            crab_factory()
        )
        g = Gebouw("1538575", 1, 4)
        g.set_gateway(crab)
        aard = g.aard
        assert isinstance(aard, Aardgebouw)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_status(self):
        crab = CrabGateway(
            crab_factory()
        )
        g = Gebouw("1538575", 1, 4)
        g.set_gateway(crab)
        status = g.status
        assert isinstance(status, Statusgebouw)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_methode(self):
        crab = CrabGateway(
            crab_factory()
        )
        g = Gebouw("1538575", 1, 4)
        g.set_gateway(crab)
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

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_lazy_load(self):
        crab = CrabGateway(
            crab_factory()
        )
        m = Metadata(
            '1830-01-01 00:00:00',
            '2003-12-06 21:42:11.117000',
            1,
            6,
            gateway=crab
        )
        assert m.begin_datum == '1830-01-01 00:00:00'
        assert m.begin_tijd == '2003-12-06 21:42:11.117000'
        assert isinstance(m.begin_bewerking, Bewerking)
        assert int(m.begin_bewerking.id) == 1
        assert isinstance(m.begin_organisatie, Organisatie)
        assert int(m.begin_organisatie.id) == 6


class TestSubadres:
    def test_fully_initialised(self):
        s = Subadres(
            1120936,
            "A",
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
        assert s.subadres == "A"
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
        assert 'A (1120936)' == str(s)
        assert "Subadres(1120936, 3, 'A', 38020)" == repr(s)

    def test_str_dont_lazy_load(self):
        s = Subadres(1120936, 'A', 3)
        assert 'A (1120936)' == str(s)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_lazy_load(self):
        crab = CrabGateway(
            crab_factory()
        )
        s = Subadres(1120936, 'A', 3)
        s.set_gateway(crab)
        assert s.id == 1120936
        assert int(s.status.id) == 3
        assert s.subadres == "A"
        assert isinstance(s.aard, Aardsubadres)
        assert int(s.huisnummer.id) == 38020
        s.metadata.set_gateway(crab)
        assert isinstance(s.metadata, Metadata)
        assert not s.metadata.begin_datum == None
        assert not s.metadata.begin_tijd == None
        assert isinstance(s.metadata.begin_bewerking, Bewerking)
        assert int(s.metadata.begin_bewerking.id) == 3
        assert isinstance(s.metadata.begin_organisatie, Organisatie)
        assert int(s.metadata.begin_organisatie.id) == 1

    def test_check_gateway_not_set(self):
        s = Subadres(1, 3, 'A', 129462)
        with pytest.raises(RuntimeError):
            s.check_gateway()

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_adresposities(self):
        crab = CrabGateway(
            crab_factory()
        )
        s = Subadres(1120936, 'A', 3)
        s.set_gateway(crab)
        adresposities = s.adresposities
        assert isinstance(adresposities, list)


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

    def test_str_dont_lazy_load(self):
        a = Adrespositie(4087928, 2)
        a.set_gateway(CrabGateway(crab_factory()))
        assert 'Adrespositie 4087928' == str(a)

    @pytest.mark.skipif(
        not pytest.config.getoption('--crab-integration'),
        reason='No CRAB Integration tests required'
    )
    def test_lazy_load(self):
        crab = CrabGateway(
            crab_factory()
        )
        a = Adrespositie(4087928, 2)
        a.set_gateway(crab)
        assert a.id == 4087928
        assert a.herkomst_id == 2
        assert str(a.geometrie) == str('POINT (190705.34 224675.26)')
        assert int(a.aard.id) == 2
        assert isinstance(a.metadata, Metadata)
        assert a.metadata.begin_datum == '1830-01-01 00:00:00'

    def test_check_gateway_not_set(self):
        a = Adrespositie(4087928, 2)
        with pytest.raises(RuntimeError):
            a.check_gateway()


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
        assert (res[0].gewest.id, 2)

    def test_get_provincie_by_id(self):
        res = self.crab.get_provincie_by_id(10000)
        assert isinstance(res, Provincie)
        assert self.crab.caches['permanent'].get('GetProvincieByProvincieNiscode#10000') == res

    def test_list_gemeenten_default_is_Vlaanderen(self):
        res = self.crab.list_gemeenten()
        assert isinstance(res, list)
        assert self.crab.caches['permanent'].get('ListGemeentenByGewestId#2#1') == res
        assert (res[0].gewest.id, 2)

    def test_list_gemeenten_gewest_1(self):
        gewest = Gewest(1)
        r = self.crab.list_gemeenten(gewest)
        assert isinstance(r, list)
        assert self.crab.caches['permanent'].get('ListGemeentenByGewestId#1#1') == r
        assert (r[0].gewest.id, 1)

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
        res = self.crab.get_adrespositie_by_id(4087928)
        assert isinstance(res, Adrespositie)
        assert str(self.crab.caches['short'].get('GetAdrespositieByAdrespositieId#4087928')) == str(res)
