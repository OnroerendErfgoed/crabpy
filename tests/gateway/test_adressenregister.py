from unittest.mock import Mock

import pytest

import tests
from crabpy.gateway import adressenregister
from crabpy.gateway.adressenregister import Adres
from crabpy.gateway.adressenregister import Deelgemeente
from crabpy.gateway.adressenregister import Gebouw
from crabpy.gateway.adressenregister import Gemeente
from crabpy.gateway.adressenregister import Gewest
from crabpy.gateway.adressenregister import Perceel
from crabpy.gateway.adressenregister import Provincie
from crabpy.gateway.adressenregister import Straat
from crabpy.gateway.exception import GatewayResourceNotFoundException


@pytest.fixture()
def client():
    return Mock()


@pytest.fixture()
def gateway(client):
    return adressenregister.Gateway(client)


def create_client_list_gemeenten_item():
    return {
        "identificator": {
            "id": "https://data.vlaanderen.be/id/gemeente/54007",
            "naamruimte": "https://data.vlaanderen.be/id/gemeente",
            "objectId": "54007",
            "versieId": "2002-08-13T16:33:18+02:00",
        },
        "detail": "https://api.basisregisters.vlaanderen.be/v1/gemeenten/54007",
        "gemeentenaam": {
            "geografischeNaam": {"spelling": "Mouscron", "taal": "fr"}
        },
        "gemeenteStatus": "inGebruik",
    }


def create_client_get_gemeente_item():
    return {
        "identificator": {
            "id": "https://data.vlaanderen.be/id/gemeente/54007",
            "naamruimte": "https://data.vlaanderen.be/id/gemeente",
            "objectId": "54007",
            "versieId": "2002-08-13T16:33:18+02:00",
        },
        "officieleTalen": ["fr"],
        "faciliteitenTalen": ["nl"],
        "gemeentenamen": [
            {"spelling": "Moeskroen", "taal": "nl"},
            {"spelling": "Mouscron", "taal": "fr"},
        ],
        "gemeenteStatus": "inGebruik",
    }


def create_client_list_straatnamen_item():
    return {
        "identificator": {
            "id": "https://data.vlaanderen.be/id/straatnaam/1",
            "naamruimte": "https://data.vlaanderen.be/id/straatnaam",
            "objectId": "1",
            "versieId": "2011-04-29T13:34:14+02:00",
        },
        "detail": "https://api.basisregisters.vlaanderen.be/v1/straatnamen/1",
        "straatnaam": {
            "geografischeNaam": {"spelling": "Acacialaan", "taal": "nl"}
        },
        "straatnaamStatus": "inGebruik",
    }


def create_client_get_straatnaam_item():
    return {
        "identificator": {
            "id": "https://data.vlaanderen.be/id/straatnaam/748",
            "naamruimte": "https://data.vlaanderen.be/id/straatnaam",
            "objectId": "748",
            "versieId": "2011-04-29T13:34:14+02:00",
        },
        "gemeente": {
            "objectId": "11002",
            "detail": "https://api.basisregisters.vlaanderen.be/v1/gemeenten/11002",
            "gemeentenaam": {
                "geografischeNaam": {"spelling": "Antwerpen", "taal": "nl"}
            },
        },
        "straatnamen": [{"spelling": "Edelvalklaan", "taal": "nl"}],
        "homoniemToevoegingen": [],
        "straatnaamStatus": "inGebruik",
    }


def create_client_list_adressen_item():
    return {
        "identificator": {
            "id": "https://data.vlaanderen.be/id/adres/200001",
            "naamruimte": "https://data.vlaanderen.be/id/adres",
            "objectId": "200001",
            "versieId": "2011-04-29T14:51:01+02:00",
        },
        "detail": "https://api.basisregisters.vlaanderen.be/v1/adressen/200001",
        "huisnummer": "59",
        "volledigAdres": {
            "geografischeNaam": {
                "spelling": "Goorbaan 59, 2230 Herselt",
                "taal": "nl",
            }
        },
        "adresStatus": "inGebruik",
    }


def create_client_get_adres_item():
    return {
        "identificator": {
            "id": "https://data.vlaanderen.be/id/adres/763445",
            "naamruimte": "https://data.vlaanderen.be/id/adres",
            "objectId": "763445",
            "versieId": "2011-04-29T14:57:43+02:00",
        },
        "gemeente": {
            "objectId": "11001",
            "detail": "https://api.basisregisters.vlaanderen.be/v1/gemeenten/11001",
            "gemeentenaam": {
                "geografischeNaam": {"spelling": "Aartselaar", "taal": "nl"}
            },
        },
        "postinfo": {
            "objectId": "2630",
            "detail": "https://api.basisregisters.vlaanderen.be/v1/postinfo/2630",
        },
        "straatnaam": {
            "objectId": "93",
            "detail": "https://api.basisregisters.vlaanderen.be/v1/straatnamen/93",
            "straatnaam": {
                "geografischeNaam": {"spelling": "Oudestraat", "taal": "nl"}
            },
        },
        "huisnummer": "27",
        "volledigAdres": {
            "geografischeNaam": {
                "spelling": "Oudestraat 27, 2630 Aartselaar",
                "taal": "nl",
            }
        },
        "adresPositie": {
            "point": {"coordinates": [150949.49, 203818.71], "type": "Point"}
        },
        "positieGeometrieMethode": "afgeleidVanObject",
        "positieSpecificatie": "gebouweenheid",
        "adresStatus": "inGebruik",
        "officieelToegekend": True,
    }


def create_client_get_perceel_item():
    return {
        "identificator": {
            "id": "https://data.vlaanderen.be/id/perceel/11001B0009-00H004",
            "naamruimte": "https://data.vlaanderen.be/id/perceel",
            "objectId": "11001B0009-00H004",
            "versieId": "2004-02-13T10:12:36+01:00",
        },
        "perceelStatus": "gerealiseerd",
        "adressen": [
            {"objectId": "763445", "detail": "https://test.be/v1/adressen/763445"}
        ],
    }


def create_client_get_gebouw_item():
    return {
        "identificator": {
            "id": "https://data.vlaanderen.be/id/gebouw/5666547",
            "naamruimte": "https://data.vlaanderen.be/id/gebouw",
            "objectId": "5666547",
            "versieId": "2011-04-29T13:11:28+02:00",
        },
        "geometriePolygoon": {
            "polygon": {
                "coordinates": [[[140284.15277253836, 186724.74131567031]]],
                "type": "Polygon",
            }
        },
        "geometrieMethode": "ingemetenGRB",
        "gebouwStatus": "gerealiseerd",
        "gebouweenheden": [],
        "percelen": [
            {
                "objectId": "23052A0059-00C000",
                "detail": "https://test.be/v1/percelen/23052A0059-00C000",
            }
        ],
    }


class TestAdressenRegisterGateway:

    def test_list_gewesten(self, gateway):
        res = gateway.list_gewesten()
        assert len(res) == 3
        assert [gewest.naam for gewest in res] == [
            "Brussels Hoofdstedelijk Gewest",
            "Vlaams Gewest",
            "Waals Gewest",
        ]

    def test_get_gewest_by_id(self, gateway):
        res = gateway.get_gewest_by_id(2)
        assert isinstance(res, Gewest)
        assert res.id == 2
        assert res.naam == "Vlaams Gewest"
        assert len(res.provincies) == 5
        assert res.centroid == [138165.09, 189297.53]
        assert res.bounding_box == [22279.17, 153050.23, 258873.3, 244022.31]

    def test_list_provincies(self, gateway):
        res = gateway.list_provincies()
        assert len(res) == 5
        assert [p.niscode for p in res] == ["10000", "20001", "30000", "40000", "70000"]

    def test_get_provincie_by_id(self, gateway):
        res = gateway.get_provincie_by_id("10000")
        assert res.niscode == "10000"
        assert res.naam == "Antwerpen"

    def test_list_gemeenten_by_provincie(self, gateway, client):
        one = create_client_list_gemeenten_item()
        two = create_client_list_gemeenten_item()
        one["identificator"]["objectId"] = "10001"
        two["identificator"]["objectId"] = "20001"
        client.get_gemeenten.return_value = [one, two]
        res = gateway.list_gemeenten_by_provincie(
            Provincie("10000", "antwerpen", 2, gateway)
        )
        assert len(res) == 1
        assert res[0].niscode == "10001"

    def test_get_gewest_by_unexisting_id(self, gateway):
        with pytest.raises(GatewayResourceNotFoundException):
            gateway.get_gewest_by_id(5)

    def test_list_gemeenten_default(self, gateway, client):
        one = create_client_list_gemeenten_item()
        two = create_client_list_gemeenten_item()
        three = create_client_list_gemeenten_item()
        one["identificator"]["objectId"] = "10001"
        two["identificator"]["objectId"] = "20001"
        three["identificator"]["objectId"] = "60001"
        client.get_gemeenten.return_value = [one, two, three]
        res = gateway.list_gemeenten()
        assert len(res) == 2
        assert [gemeente.niscode for gemeente in res] == ["10001", "20001"]

    def test_get_gemeente_by_id(self, gateway, client):
        client.get_gemeente.return_value = create_client_get_gemeente_item()
        res = gateway.get_gemeente_by_id(1)
        assert res.niscode == "54007"
        assert res.naam == "Moeskroen"

    def test_get_gemeente_by_niscode(self, gateway, client):
        client.get_gemeente.return_value = create_client_get_gemeente_item()
        res = gateway.get_gemeente_by_niscode(1)
        assert res.niscode == "54007"
        assert res.naam == "Moeskroen"

    def test_list_deelgemeenten(self, gateway):
        res = gateway.list_deelgemeenten()
        assert len(res) == 1132
        assert res[0].naam == "Aartselaar"
        assert res[0].id == "11001A"
        assert res[0].gemeente_niscode == "11001"

    def test_list_deelgemeenten_by_gemeente(self, gateway):
        res = gateway.list_deelgemeenten_by_gemeente(
            Gemeente(niscode="11001", naam="Aartselaar", taal="nl", gateway=gateway)
        )
        assert len(res) == 1
        assert res[0].naam == "Aartselaar"
        assert res[0].id == "11001A"
        assert res[0].gemeente_niscode == "11001"

    def test_get_deelgemeente_by_id(self, gateway):
        res = gateway.get_deelgemeente_by_id("11001A")
        assert res.naam == "Aartselaar"
        assert res.id == "11001A"
        assert res.gemeente_niscode == "11001"

    def test_list_straten(self, gateway, client):
        client.get_straatnamen.return_value = [
            create_client_list_straatnamen_item(),
            create_client_list_straatnamen_item(),
        ]
        res = gateway.list_straten(Gemeente("Aartselaar", "11001", "nl", gateway))
        assert len(res) == 2
        assert res[0].id == "1"
        assert res[0].naam == "Acacialaan"
        assert res[0].status == "inGebruik"
        assert res[0].taal == "nl"

    def test_get_straat_by_id(self, gateway, client):
        client.get_straatnaam.return_value = create_client_get_straatnaam_item()
        res = gateway.get_straat_by_id(1)
        assert res.id == "748"
        assert res.naam == "Edelvalklaan"
        assert res.status == "inGebruik"
        assert res.taal == "nl"

    def test_list_adressen_by_straat(self, gateway, client):
        client.get_adressen.return_value = [
            create_client_list_adressen_item(),
            create_client_list_adressen_item(),
        ]
        res = gateway.list_adressen_by_straat(
            Straat("1", "inGebruik", "straatnaaam", "nl", gateway)
        )
        assert len(res) == 2
        assert res[0].id == "200001"
        assert res[0].huisnummer == "59"
        assert res[0].label == "Goorbaan 59, 2230 Herselt"
        assert res[0].status == "inGebruik"
        assert res[0].taal == "nl"

    def test_list_adressen_by_perceel(self, gateway, client):
        client.get_adres.return_value = create_client_get_adres_item()
        client.get_perceel.return_value = create_client_get_perceel_item()
        res = gateway.list_adressen_by_perceel(
            Perceel(
                id_="1",
                status="inGebruik",
                gateway=gateway,
            )
        )
        assert len(res) == 1
        assert res[0].id == "763445"

    def test_get_perceel_by_id(self, gateway, client):
        client.get_perceel.return_value = create_client_get_perceel_item()
        res = gateway.get_perceel_by_id("1")
        assert res.id == '11001B0009-00H004'

    def test_get_gebouw_by_id(self, gateway, client):
        client.get_gebouw.return_value = create_client_get_gebouw_item()
        res = gateway.get_gebouw_by_id("1")
        assert res.geojson == {
            "polygon": {
                "coordinates": [[[140284.15277253836, 186724.7413156703]]],
                "type": "Polygon",
            }
        }
        assert res.id == "5666547"
        assert len(res.percelen) == 1
        assert res.percelen[0].id == "23052A0059-00C000"
        assert res.status == "gerealiseerd"


class TestGewest:

    def test_gemeenten(self, gateway, client):
        one = create_client_list_gemeenten_item()
        two = create_client_list_gemeenten_item()
        three = create_client_list_gemeenten_item()
        one["identificator"]["objectId"] = "10001"
        two["identificator"]["objectId"] = "20001"
        three["identificator"]["objectId"] = "60001"
        client.get_gemeenten.return_value = [one, two, three]

        vlaanderen = gateway.get_gewest_by_id(2)
        res = vlaanderen.gemeenten
        assert len(res) == 2
        assert [gemeente.niscode for gemeente in res] == ["10001", "20001"]

    def test_provincies(self, gateway):
        vlaanderen = gateway.get_gewest_by_id(2)
        provincies = vlaanderen.provincies
        assert len(provincies) == 5


class TestProvincie:

    def test_gemeenten(self, gateway, client):
        one = create_client_list_gemeenten_item()
        two = create_client_list_gemeenten_item()
        one["identificator"]["objectId"] = "10001"
        two["identificator"]["objectId"] = "20001"
        client.get_gemeenten.return_value = [one, two]

        p = Provincie("10001", "Antwerpen", Gewest(2, "Vlaanderen", None, None), gateway)
        res = p.gemeenten
        assert len(res) == 1
        assert res[0].niscode == "10001"


class TestGemeente:

    def test_straten(self, gateway, client):
        client.get_straatnamen.return_value = [create_client_list_straatnamen_item()]
        g = Gemeente(niscode="1", naam="test-gemeente", gateway=gateway)
        straten = g.straten
        assert len(straten) == 1
        assert straten[0].id == "1"

    def test_provincie(self, gateway):
        g = Gemeente(niscode="1", naam="test-gemeente", gateway=gateway)
        provincie = g.provincie
        assert provincie.naam == "Antwerpen"

    def test_taal(self, gateway, client):
        client.get_gemeente.return_value = create_client_get_gemeente_item()
        g = Gemeente(niscode="1", gateway=gateway)
        assert g.taal == "nl"

    def test_naam(self, gateway, client):
        client.get_gemeente.return_value = create_client_get_gemeente_item()
        g = Gemeente(niscode="1", gateway=gateway)
        assert g.naam == "Moeskroen"

    def test_caching_and_lazy_loading(self, gateway, client):
        client.get_gemeente.return_value = create_client_get_gemeente_item()
        gemeente = Gemeente(niscode="1", gateway=gateway)
        assert gemeente.naam == "Moeskroen"
        assert gemeente.naam == "Moeskroen"
        assert client.get_gemeente.call_count == 1
        gemeente = Gemeente(niscode="1", gateway=gateway)
        assert gemeente.naam == "Moeskroen"
        assert client.get_gemeente.call_count == 2
        with tests.memory_cache():
            gemeente = Gemeente(niscode="1", gateway=gateway)
            assert gemeente.naam == "Moeskroen"
            assert gemeente.naam == "Moeskroen"
            gemeente = Gemeente(niscode="1", gateway=gateway)
            assert gemeente.naam == "Moeskroen"
            assert client.get_gemeente.call_count == 3

            gemeente = Gemeente(niscode="2", gateway=gateway)
            assert gemeente.naam == "Moeskroen"
            assert client.get_gemeente.call_count == 4


class TestDeelgemeente:

    def test_gemeente(self, gateway):
        dg = Deelgemeente(
            id_="45062A",
            naam="Sint-Maria-Horebeke",
            gemeente_niscode="45062",
            gateway=None
        )
        gemeente = dg.gemeente
        assert isinstance(gemeente, Gemeente)
        assert gemeente.niscode == "45062"


class TestStraat:

    def test_adressen(self, gateway, client):
        client.get_adressen.return_value = [
            create_client_list_adressen_item()
        ]
        straat = Straat(id_=1, naam="straatnaam", gateway=gateway)
        adressen = straat.adressen
        assert len(adressen) == 1
        assert adressen[0].id == "200001"

    def test_taal(self, gateway, client):
        client.get_straatnaam.return_value = create_client_get_straatnaam_item()
        s = Straat(id_=1, gateway=gateway)
        assert s.taal == "nl"

    def test_gemeente(self, gateway, client):
        client.get_straatnaam.return_value = create_client_get_straatnaam_item()
        s = Straat(id_=1, gateway=gateway)
        assert s.gemeente.niscode == "11002"

    def test_status(self, gateway, client):
        client.get_straatnaam.return_value = create_client_get_straatnaam_item()
        s = Straat(id_=1, gateway=gateway)
        assert s.status == "inGebruik"


class TestAdres:

    def test_adres(self, gateway, client):
        client.get_adres.return_value = create_client_get_adres_item()
        adres = Adres(id_="1", gateway=gateway)
        assert adres.label == "Oudestraat 27, 2630 Aartselaar"
        assert adres.taal == "nl"
        assert adres.huisnummer == "27"

    def test_gemeente(self, gateway, client):
        client.get_adres.return_value = create_client_get_adres_item()
        adres = Adres(id_="1", gateway=gateway)
        gemeente = adres.gemeente
        assert gemeente.niscode == "11001"


class TestPerceel:

    def test_adressen(self, gateway, client):
        client.get_perceel.return_value = create_client_get_perceel_item()
        perceel = Perceel(id_="1", gateway=gateway)
        adressen = perceel.adressen
        assert len(adressen) == 1
        assert adressen[0].id == "763445"

    def test_status(self, gateway, client):
        client.get_perceel.return_value = create_client_get_perceel_item()
        perceel = Perceel(id_="1", gateway=gateway)
        assert perceel.status == "gerealiseerd"


class TestGebouw:

    def test_gebouw(self, gateway, client):
        client.get_gebouw.return_value = create_client_get_gebouw_item()
        gebouw = Gebouw(id_=1, gateway=gateway)
        assert gebouw.status == "gerealiseerd"
        assert gebouw.geojson == {
            'polygon': {
                'coordinates': [[[140284.15277253836, 186724.7413156703]]],
                'type': 'Polygon'
            }
        }

    def test_percelen(self, gateway, client):
        client.get_gebouw.return_value = create_client_get_gebouw_item()
        gebouw = Gebouw(id_=1, gateway=gateway)
        percelen = gebouw.percelen
        assert len(percelen) == 1
        assert percelen[0].id == "23052A0059-00C000"
