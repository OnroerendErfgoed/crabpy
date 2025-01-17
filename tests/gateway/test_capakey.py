import re
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import requests

from crabpy.gateway.capakey import Afdeling
from crabpy.gateway.capakey import GatewayRuntimeException
from crabpy.gateway.capakey import Gemeente
from crabpy.gateway.capakey import Perceel
from crabpy.gateway.capakey import Sectie
from crabpy.gateway.capakey import capakey_rest_gateway_request
from tests.conftest import CAPAKEY_URL


def connection_error(url, headers=None, params=None):
    raise requests.exceptions.ConnectionError


def request_exception(url, headers=None, params=None):
    raise requests.exceptions.RequestException


class TestCapakeyRestGateway:
    def test_list_gemeenten(self, capakey_rest_gateway, municipalities_response):
        res = capakey_rest_gateway.list_gemeenten()
        assert isinstance(res, list)

    def test_get_gemeente_by_id(self, capakey_rest_gateway, municipality_response):
        res = capakey_rest_gateway.get_gemeente_by_id(44021)
        assert isinstance(res, Gemeente)
        assert res.id == 44021

    def test_get_gemeente_by_invalid_id(self, capakey_rest_gateway, mocked_responses):
        url = re.compile(rf"{CAPAKEY_URL}/municipality/[^/]+\?")
        mocked_responses.add(method="GET", url=url, status=404)
        from crabpy.gateway.exception import GatewayResourceNotFoundException

        with pytest.raises(GatewayResourceNotFoundException):
            capakey_rest_gateway.get_gemeente_by_id("gent")

    def test_list_afdelingen(
        self,
        capakey_rest_gateway,
        municipalities_response,
        municipality_department_response,
    ):
        res = capakey_rest_gateway.list_kadastrale_afdelingen()
        assert isinstance(res, list)
        assert len(res) > 300

    def test_list_afdelingen_by_gemeente(
        self,
        capakey_rest_gateway,
        municipality_response,
        municipality_department_response,
    ):
        g = capakey_rest_gateway.get_gemeente_by_id(44021)
        res = capakey_rest_gateway.list_kadastrale_afdelingen_by_gemeente(g)
        assert isinstance(res, list)
        assert len(res) > 0
        assert len(res) < 40

    def test_list_afdelingen_by_gemeente_id(
        self,
        capakey_rest_gateway,
        municipality_response,
        municipality_department_response,
    ):
        res = capakey_rest_gateway.list_kadastrale_afdelingen_by_gemeente(44021)
        assert isinstance(res, list)
        assert len(res) > 0
        assert len(res) < 40

    def test_get_kadastrale_afdeling_by_id(
        self, capakey_rest_gateway, department_response
    ):
        res = capakey_rest_gateway.get_kadastrale_afdeling_by_id(44021)
        assert isinstance(res, Afdeling)
        assert res.id == 44021
        assert isinstance(res.gemeente, Gemeente)
        assert res.gemeente.id == 44021

    def test_list_secties_by_afdeling(
        self, capakey_rest_gateway, department_response, department_sections_response
    ):
        a = capakey_rest_gateway.get_kadastrale_afdeling_by_id(44021)
        res = capakey_rest_gateway.list_secties_by_afdeling(a)
        assert isinstance(res, list)
        assert len(res) == 1

    def test_list_secties_by_afdeling_id(
        self, capakey_rest_gateway, department_response, department_sections_response
    ):
        res = capakey_rest_gateway.list_secties_by_afdeling(44021)
        assert isinstance(res, list)
        assert len(res) == 1

    def test_get_sectie_by_id_and_afdeling(
        self, capakey_rest_gateway, department_response, department_section_response
    ):
        a = capakey_rest_gateway.get_kadastrale_afdeling_by_id(44021)
        res = capakey_rest_gateway.get_sectie_by_id_and_afdeling("A", a)
        assert isinstance(res, Sectie)
        assert res.id == "A"
        assert res.afdeling.id == 44021

    def test_list_percelen_by_sectie(
        self,
        capakey_rest_gateway,
        department_response,
        department_section_response,
        department_section_parcels_response,
    ):
        s = capakey_rest_gateway.get_sectie_by_id_and_afdeling("A", 44021)
        res = capakey_rest_gateway.list_percelen_by_sectie(s)
        assert isinstance(res, list)
        assert len(res) > 0

    def test_get_perceel_by_id_and_sectie(
        self,
        capakey_rest_gateway,
        department_response,
        department_section_response,
        department_section_parcels_response,
        department_section_parcel_response,
    ):
        s = capakey_rest_gateway.get_sectie_by_id_and_afdeling("A", 44021)
        percelen = capakey_rest_gateway.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = capakey_rest_gateway.get_perceel_by_id_and_sectie(perc.id, s)
        assert isinstance(res, Perceel)
        assert res.sectie.id == "A"
        assert res.sectie.afdeling.id == 44021

    def test_get_perceel_by_capakey(
        self,
        capakey_rest_gateway,
        department_response,
        department_section_response,
        department_section_parcels_response,
        parcel_response,
    ):
        s = capakey_rest_gateway.get_sectie_by_id_and_afdeling("A", 44021)
        percelen = capakey_rest_gateway.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = capakey_rest_gateway.get_perceel_by_capakey(perc.capakey)
        assert isinstance(res, Perceel)
        assert res.sectie.id == "A"
        assert res.sectie.afdeling.id == 44021
        assert res.centroid == (104036.06610000134, 194676.8699000012)
        assert res.bounding_box == (
            104029.2602000013,
            194665.0236000009,
            104042.87200000137,
            194688.71620000154,
        )
        assert res.shape is not None

    def test_get_perceel_by_coordinates(self, capakey_rest_gateway, parcels_response):
        res = capakey_rest_gateway.get_perceel_by_coordinates(104036, 194676)
        assert isinstance(res, Perceel)
        assert res.sectie.id == "A"
        assert res.sectie.afdeling.id == 44021
        assert res.centroid == (104036.06610000134, 194676.8699000012)
        assert res.bounding_box == (
            104029.2602000013,
            194665.0236000009,
            104042.87200000137,
            194688.71620000154,
        )
        assert res.shape is not None

    def test_get_perceel_by_percid(
        self,
        capakey_rest_gateway,
        department_response,
        department_section_response,
        department_section_parcels_response,
        parcel_response,
    ):
        s = capakey_rest_gateway.get_sectie_by_id_and_afdeling("A", 44021)
        percelen = capakey_rest_gateway.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = capakey_rest_gateway.get_perceel_by_percid(perc.percid)
        assert isinstance(res, Perceel)
        assert res.sectie.id == "A"
        assert res.sectie.afdeling.id == 44021

    @patch("requests.get", MagicMock(side_effect=connection_error))
    def test_requests_connection(self):
        with pytest.raises(GatewayRuntimeException) as cm:
            capakey_rest_gateway_request("url")
        exception = cm.value.message
        expected = (
            "Could not execute request due to connection problems:\nConnectionError()"
        )
        assert exception == expected

    @patch("requests.get", MagicMock(side_effect=request_exception))
    def test_requests_request_exception(self):
        with pytest.raises(GatewayRuntimeException) as cm:
            capakey_rest_gateway_request("url")
        exception = cm.value.message
        assert exception == "Could not execute request due to:\nRequestException()"


class TestGemeente:
    def test_fully_initialised(self):
        g = Gemeente(
            44021,
            "Gent",
            (104154.2225, 197300.703),
            (94653.453, 185680.984, 113654.992, 208920.422),
        )
        assert g.id == 44021
        assert g.naam == "Gent"
        assert g.centroid == (104154.2225, 197300.703)
        assert g.bounding_box == (94653.453, 185680.984, 113654.992, 208920.422)
        assert "Gent (44021)" == str(g)
        assert "Gemeente(44021, 'Gent')" == repr(g)

    def test_str_and_repr_dont_lazy_load(self):
        g = Gemeente(44021, "Gent")
        assert "Gent (44021)" == str(g)
        assert "Gemeente(44021, 'Gent')" == repr(g)

    def test_check_gateway_not_set(self):
        g = Gemeente(44021, "Gent")
        with pytest.raises(RuntimeError):
            g.check_gateway()

    def test_lazy_load_1(self, capakey_rest_gateway):
        g = Gemeente(44021, "Gent", gateway=capakey_rest_gateway)
        g.clear_gateway()
        with pytest.raises(RuntimeError):
            g.check_gateway()

    def test_lazy_load(self, capakey_rest_gateway, municipality_response):
        g = Gemeente(44021, "Gent")
        g.set_gateway(capakey_rest_gateway)
        assert g.id == 44021
        assert g.naam == "Gent"
        assert g.centroid is not None
        assert g.bounding_box is not None

    def test_afdelingen(self, capakey_rest_gateway, municipality_department_response):
        g = Gemeente(44021, "Gent")
        g.set_gateway(capakey_rest_gateway)
        afdelingen = g.afdelingen
        assert isinstance(afdelingen, list)
        assert len(afdelingen) > 0
        assert len(afdelingen) < 40


class TestAfdeling:
    def test_fully_initialised(self):
        a = Afdeling(
            44021,
            "GENT  1 AFD",
            Gemeente(44021, "Gent"),
            (104893.06375, 196022.244094),
            (104002.076625, 194168.3415, 105784.050875, 197876.146688),
        )
        assert a.id == 44021
        assert a.naam == "GENT  1 AFD"
        assert a.centroid == (104893.06375, 196022.244094)
        assert a.bounding_box == (
            104002.076625,
            194168.3415,
            105784.050875,
            197876.146688,
        )
        assert "GENT  1 AFD (44021)" == str(a)
        assert "Afdeling(44021, 'GENT  1 AFD')" == repr(a)

    def test_partially_initialised(self):
        a = Afdeling(
            44021,
            "GENT  1 AFD",
            Gemeente(44021, "Gent"),
        )
        assert a.id == 44021
        assert a.naam == "GENT  1 AFD"
        assert "GENT  1 AFD (44021)" == str(a)
        assert "Afdeling(44021, 'GENT  1 AFD')" == repr(a)

    def test_to_string_not_fully_initialised(self):
        a = Afdeling(44021)
        assert "Afdeling 44021" == str(a)

    def test_check_gateway_not_set(self):
        a = Afdeling(44021)
        with pytest.raises(RuntimeError):
            a.check_gateway()

    def test_lazy_load(self, capakey_rest_gateway, department_response):
        a = Afdeling(44021)
        a.set_gateway(capakey_rest_gateway)
        assert a.id == 44021
        assert a.naam == "GENT  1 AFD"
        assert a.centroid is not None
        assert a.bounding_box is not None

    def test_secties(
        self, capakey_rest_gateway, department_response, department_sections_response
    ):
        a = Afdeling(44021)
        a.set_gateway(capakey_rest_gateway)
        secties = a.secties
        assert isinstance(secties, list)
        assert len(secties) == 1


class TestSectie:
    def test_fully_initialised(self):
        s = Sectie(
            "A",
            Afdeling(44021, "Gent  1 AFD"),
            (104893.06375, 196022.244094),
            (104002.076625, 194168.3415, 105784.050875, 197876.146688),
        )
        assert s.id == "A"
        assert s.centroid == (104893.06375, 196022.244094)
        assert s.bounding_box == (
            104002.076625,
            194168.3415,
            105784.050875,
            197876.146688,
        )
        assert "Gent  1 AFD (44021), Sectie A" == str(s)
        assert "Sectie('A', Afdeling(44021, 'Gent  1 AFD'))" == repr(s)

    def test_check_gateway_not_set(self):
        s = Sectie("A", Afdeling(44021))
        with pytest.raises(RuntimeError):
            s.check_gateway()

    def test_clear_gateway(self, capakey_rest_gateway):
        s = Sectie("A", Afdeling(44021))
        s.set_gateway(capakey_rest_gateway)
        s.check_gateway()
        s.clear_gateway()
        with pytest.raises(RuntimeError):
            s.check_gateway()

    def test_lazy_load(
        self, capakey_rest_gateway, department_response, department_section_response
    ):
        s = Sectie("A", Afdeling(44021))
        s.set_gateway(capakey_rest_gateway)
        assert s.id == "A"
        assert s.afdeling.id == 44021
        assert s.centroid is not None
        assert s.bounding_box is not None

    def test_percelen(
        self,
        capakey_rest_gateway,
        department_response,
        department_section_parcels_response,
    ):
        s = Sectie("A", Afdeling(44021))
        s.set_gateway(capakey_rest_gateway)
        percelen = s.percelen
        assert isinstance(percelen, list)
        assert len(percelen) > 0


class TestPerceel:
    def test_fully_initialised(self):
        p = Perceel(
            "1154/02C000",
            Sectie("A", Afdeling(46013)),
            "40613A1154/02C000",
            "40613_A_1154_C_000_02",
            ["Teststraat 10, 2000 Gemeente"],
            "capaty",
            "cashkey",
            (104893.06375, 196022.244094),
            (104002.076625, 194168.3415, 105784.050875, 197876.146688),
        )
        assert p.id == ("1154/02C000")
        assert p.sectie.id == "A"
        assert p.capatype == "capaty"
        assert p.cashkey == "cashkey"
        assert p.centroid == (104893.06375, 196022.244094)
        assert p.bounding_box == (
            104002.076625,
            194168.3415,
            105784.050875,
            197876.146688,
        )
        assert p.capakey == str(p)
        assert p.adres == ["Teststraat 10, 2000 Gemeente"]
        assert (
            "Perceel('1154/02C000', Sectie('A', Afdeling(46013)), "
            "'40613A1154/02C000', '40613_A_1154_C_000_02')" == repr(p)
        )

    def test_check_gateway_not_set(self):
        p = Perceel(
            "1154/02C000",
            Sectie("A", Afdeling(46013)),
            "40613A1154/02C000",
            "40613_A_1154_C_000_02",
        )
        with pytest.raises(RuntimeError):
            p.check_gateway()

    def test_clear_gateway(self, capakey_rest_gateway):
        p = Perceel(
            "1154/02C000",
            Sectie("A", Afdeling(46013)),
            "40613A1154/02C000",
            "40613_A_1154_C_000_02",
        )
        p.set_gateway(capakey_rest_gateway)
        p.check_gateway()
        p.sectie.check_gateway()
        p.clear_gateway()
        with pytest.raises(RuntimeError):
            p.sectie.check_gateway()
            p.check_gateway()

    def test_lazy_load(
        self,
        capakey_rest_gateway,
        department_response,
        department_section_parcel_response,
    ):
        p = Perceel(
            "1154/02C000",
            Sectie("A", Afdeling(46013)),
            "46013A1154/02C000",
            "46013_A_1154_C_000_02",
            gateway=capakey_rest_gateway,
        )
        assert p.id == "1154/02C000"
        assert p.sectie.id == "A"
        assert p.sectie.afdeling.id == 46013
        assert p.capatype is None
        assert p.cashkey is None
        assert p.centroid is not None
        assert p.bounding_box is not None

    def test_parse_capakey(self):
        p = Perceel(
            "1154/02C000",
            Sectie("A", Afdeling(46013)),
            "46013A1154/02C000",
            "46013_A_1154_C_000_02",
        )
        assert p.grondnummer == "1154"
        assert p.bisnummer == "02"
        assert p.exponent == "C"
        assert p.macht == "000"

    def test_parse_capakey_other_sectie(self):
        p = Perceel(
            "1154/02C000",
            Sectie("F", Afdeling(46013)),
            "46013F1154/02C000",
            "46013_F_1154_C_000_02",
        )
        assert p.grondnummer == "1154"
        assert p.bisnummer == "02"
        assert p.exponent == "C"
        assert p.macht == "000"

    def test_parse_invalid_capakey(self):
        with pytest.raises(ValueError):
            Perceel(
                "1154/02C000",
                Sectie("A", Afdeling(46013)),
                "46013_A_1154_C_000_02",
                "46013A1154/02C000",
            )

    def test_from_capakey_to_percid_and_back(self):
        assert (
            Perceel.get_percid_from_capakey("46013A1154/02C000")
            == "46013_A_1154_C_000_02"
        )
        assert (
            Perceel.get_capakey_from_percid("46013_A_1154_C_000_02")
            == "46013A1154/02C000"
        )

    def test_invalid_capakey_or_percid(self):
        with pytest.raises(ValueError):
            Perceel.get_capakey_from_percid("46013A1154/02C000")
        with pytest.raises(ValueError):
            Perceel.get_percid_from_capakey("46013_A_1154_C_000_02")
