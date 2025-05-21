from unittest.mock import Mock

import pytest

from crabpy.gateway import adressenregister
from crabpy.gateway.adressenregister import Adres
from crabpy.gateway.adressenregister import Deelgemeente
from crabpy.gateway.adressenregister import Gebouw
from crabpy.gateway.adressenregister import Gemeente
from crabpy.gateway.adressenregister import Gewest
from crabpy.gateway.adressenregister import Perceel
from crabpy.gateway.adressenregister import Postinfo
from crabpy.gateway.adressenregister import Provincie
from crabpy.gateway.adressenregister import Straat


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
        "gemeentenaam": {"geografischeNaam": {"spelling": "Mouscron", "taal": "fr"}},
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
        "straatnaam": {"geografischeNaam": {"spelling": "Acacialaan", "taal": "nl"}},
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
        "busnummer": "A",
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


def create_client_get_perceel_list_item():
    return {
        "@type": "Perceel",
        "identificator": {
            "id": "https://data.vlaanderen.be/id/perceel/13013C0384-02H003",
            "naamruimte": "https://data.vlaanderen.be/id/perceel",
            "objectId": "13013C0384-02H003",
            "versieId": "2004-02-13T05:34:17+01:00",
        },
        "detail": (
            "https://api.basisregisters.vlaanderen.be/v2/percelen/13013C0384-02H003"
        ),
        "perceelStatus": "gerealiseerd",
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


def create_client_get_post_info():
    return {
        "identificator": {
            "id": "https://data.vlaanderen.be/id/postinfo/7850",
            "naamruimte": "https://data.vlaanderen.be/id/postinfo",
            "objectId": "7850",
            "versieId": "2020-02-10T12:44:14+01:00",
        },
        "gemeente": {
            "objectId": "55010",
            "detail": "https://api.basisregisters.vlaanderen.be/v2/gemeenten/55010",
            "gemeentenaam": {"geografischeNaam": {"spelling": "Enghien", "taal": "fr"}},
        },
        "postnamen": [
            {"geografischeNaam": {"spelling": "EDINGEN", "taal": "nl"}},
            {"geografischeNaam": {"spelling": "Enghien", "taal": "fr"}},
            {"geografischeNaam": {"spelling": "Lettelingen", "taal": "nl"}},
            {"geografischeNaam": {"spelling": "Mark", "taal": "nl"}},
        ],
        "postInfoStatus": "gerealiseerd",
    }


def create_client_get_post_infos():
    return [
        {
            "@type": "PostInfo",
            "identificator": {
                "id": "https://data.vlaanderen.be/id/postinfo/1000",
                "naamruimte": "https://data.vlaanderen.be/id/postinfo",
                "objectId": "1000",
                "versieId": "2020-02-10T12:44:14+01:00",
            },
            "detail": "https://api.basisregisters.vlaanderen.be/v2/postinfo/1000",
            "postInfoStatus": "gerealiseerd",
            "postnamen": [{"geografischeNaam": {"spelling": "BRUSSEL", "taal": "nl"}}],
        },
        {
            "@type": "PostInfo",
            "identificator": {
                "id": "https://data.vlaanderen.be/id/postinfo/1020",
                "naamruimte": "https://data.vlaanderen.be/id/postinfo",
                "objectId": "1020",
                "versieId": "2020-02-10T12:44:14+01:00",
            },
            "detail": "https://api.basisregisters.vlaanderen.be/v2/postinfo/1020",
            "postInfoStatus": "gerealiseerd",
            "postnamen": [{"geografischeNaam": {"spelling": "Laken", "taal": "nl"}}],
        },
        {
            "@type": "PostInfo",
            "identificator": {
                "id": "https://data.vlaanderen.be/id/postinfo/1031",
                "naamruimte": "https://data.vlaanderen.be/id/postinfo",
                "objectId": "1031",
                "versieId": "2020-02-10T12:44:14+01:00",
            },
            "detail": "https://api.basisregisters.vlaanderen.be/v2/postinfo/1031",
            "postInfoStatus": "gerealiseerd",
            "postnamen": [
                {
                    "geografischeNaam": {
                        "spelling": "Christelijke Sociale Organisaties",
                        "taal": "nl",
                    }
                }
            ],
        },
        {
            "@type": "PostInfo",
            "identificator": {
                "id": "https://data.vlaanderen.be/id/postinfo/1041",
                "naamruimte": "https://data.vlaanderen.be/id/postinfo",
                "objectId": "1041",
                "versieId": "2020-02-10T12:44:14+01:00",
            },
            "detail": "https://api.basisregisters.vlaanderen.be/v2/postinfo/1041",
            "postInfoStatus": "gerealiseerd",
            "postnamen": [
                {
                    "geografischeNaam": {
                        "spelling": "International press center",
                        "taal": "en",
                    }
                }
            ],
        },
        {
            "@type": "PostInfo",
            "identificator": {
                "id": "https://data.vlaanderen.be/id/postinfo/1120",
                "naamruimte": "https://data.vlaanderen.be/id/postinfo",
                "objectId": "1120",
                "versieId": "2020-02-10T12:44:14+01:00",
            },
            "detail": "https://api.basisregisters.vlaanderen.be/v2/postinfo/1120",
            "postInfoStatus": "gerealiseerd",
            "postnamen": [
                {"geografischeNaam": {"spelling": "Neder-Over-Heembeek", "taal": "nl"}}
            ],
        },
        {
            "@type": "PostInfo",
            "identificator": {
                "id": "https://data.vlaanderen.be/id/postinfo/1130",
                "naamruimte": "https://data.vlaanderen.be/id/postinfo",
                "objectId": "1130",
                "versieId": "2020-02-10T12:44:14+01:00",
            },
            "detail": "https://api.basisregisters.vlaanderen.be/v2/postinfo/1130",
            "postInfoStatus": "gerealiseerd",
            "postnamen": [{"geografischeNaam": {"spelling": "Haren", "taal": "nl"}}],
        },
    ]


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
        res = gateway.get_gewest_by_niscode("2000")
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
        res = gateway.get_provincie_by_niscode("10000")
        assert res.niscode == "10000"
        assert res.naam == "Antwerpen"

    def test_list_gemeenten_by_provincie(self, gateway, client):
        res = gateway.list_gemeenten_by_provincie(
            Provincie("10000", "antwerpen", 2, gateway)
        )
        assert len(res) == 69
        assert res[0].niscode == "11001"

    def test_get_gewest_by_unexisting_id(self, gateway):
        assert gateway.get_gewest_by_niscode("5000") is None

    def test_list_gemeenten_default(self, gateway, client):
        res = gateway.list_gemeenten()
        assert len(res) == 312
        niscodes = [gemeente.niscode for gemeente in res]
        assert "11001" in niscodes
        assert "23002" in niscodes
        assert "31003" in niscodes
        assert "41002" in niscodes
        assert "41002" in niscodes
        assert "71002" in niscodes

    def test_get_gemeente_by_niscode(self, gateway, client):
        res = gateway.get_gemeente_by_niscode("57096")
        assert res.niscode == "57096"
        assert res.naam() == "Moeskroen"
        assert res.provincie.niscode == "50000"

    def test_get_gemeente_by_naam(self, gateway, client):
        res = gateway.get_gemeente_by_naam("Moeskroen")
        assert res.niscode == "57096"
        assert res.naam() == "Moeskroen"
        assert res.provincie.niscode == "50000"

    def test_get_gemeente_by_naam_filter_talen(self, gateway, client):
        res = gateway.get_gemeente_by_naam("Mouscron", talen=["nl"])
        assert res is None
        res = gateway.get_gemeente_by_naam("Mouscron", talen=["fr"])
        assert res.niscode == "57096"
        assert res.naam(taal="fr") == "Mouscron"
        assert res.provincie.niscode == "50000"

    def test_list_deelgemeenten(self, gateway):
        res = gateway.list_deelgemeenten()
        assert len(res) == 1132
        assert res[0].naam == "Aartselaar"
        assert res[0].id == "11001A"
        assert res[0].gemeente_niscode == "11001"

    def test_list_deelgemeenten_by_gemeente(self, gateway):
        res = gateway.list_deelgemeenten_by_gemeente(
            Gemeente(niscode="11001", naam="Aartselaar", gateway=gateway)
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
        res = gateway.list_straten(
            Gemeente(naam="Aartselaar", niscode="11001", gateway=gateway)
        )
        assert len(res) == 2
        assert res[0].id == "1"
        assert res[0].naam() == "Acacialaan"
        assert res[0].status == "inGebruik"

    def test_get_straat_by_id(self, gateway, client):
        client.get_straatnaam.return_value = create_client_get_straatnaam_item()
        res = gateway.get_straat_by_id(1)
        assert res.id == "748"
        assert res.naam() == "Edelvalklaan"
        assert res.status == "inGebruik"

    def test_list_adressen_by_straat(self, gateway, client):
        client.get_adressen.return_value = [
            create_client_list_adressen_item(),
            create_client_list_adressen_item(),
        ]
        res = gateway.list_adressen_by_straat(
            Straat("1", gateway, status="inGebruik", naam="straatnaaam")
        )
        assert len(res) == 2
        assert res[0].id == "200001"
        assert res[0].huisnummer == "59"
        assert res[0].label == "Goorbaan 59, 2230 Herselt"
        assert res[0].status == "inGebruik"

    def test_list_adressen_by_straat_and_huisnummer(self, gateway, client):
        client.get_adressen.return_value = [
            create_client_list_adressen_item(),
        ]
        res = gateway.list_adressen_with_params(
            straatnaamObjectId=1,
            huisnummer="59",
        )
        assert len(res) == 1
        assert res[0].id == "200001"
        assert res[0].huisnummer == "59"
        assert res[0].label == "Goorbaan 59, 2230 Herselt"
        assert res[0].status == "inGebruik"

    def test_list_percelen_by_adres(self, gateway, client):
        client.get_percelen.return_value = [
            create_client_get_perceel_list_item(),
        ]
        res = gateway.list_percelen_with_params(
            adresObjectId=200001,
        )
        assert len(res) == 1
        assert res[0].id == "13013C0384-02H003"
        assert res[0].status == "gerealiseerd"

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

    def test_get_adres_by_id(self, gateway, client):
        client.get_adres.return_value = create_client_get_adres_item()
        res = gateway.get_adres_by_id(763445)
        assert res.id == "763445"
        assert res.uri == "https://data.vlaanderen.be/id/adres/763445"

    def test_get_perceel_by_id(self, gateway, client):
        client.get_perceel.return_value = create_client_get_perceel_item()
        res = gateway.get_perceel_by_id("1")
        assert res.id == "11001B0009-00H004"
        assert res.uri == "https://data.vlaanderen.be/id/perceel/11001B0009-00H004"

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
        assert res.uri == "https://data.vlaanderen.be/id/gebouw/5666547"


class TestGewest:
    def test_gemeenten(self, gateway, client):
        vlaanderen = gateway.get_gewest_by_niscode("2000")
        res = vlaanderen.gemeenten
        assert len(res) == 312
        niscodes = [gemeente.niscode for gemeente in res]
        assert "11001" in niscodes
        assert "23002" in niscodes
        assert "31003" in niscodes
        assert "41002" in niscodes
        assert "41002" in niscodes
        assert "71002" in niscodes

    def test_provincies(self, gateway):
        vlaanderen = gateway.get_gewest_by_niscode("2000")
        provincies = vlaanderen.provincies
        assert len(provincies) == 5


class TestProvincie:
    def test_gemeenten(self, gateway, client):
        p = Provincie(
            "10000", "Antwerpen", Gewest(2, "2000", "Vlaanderen", None, None), gateway
        )
        res = p.gemeenten
        assert len(res) == 69
        assert res[0].niscode == "11001"


class TestGemeente:
    def test_straten(self, gateway, client):
        client.get_straatnamen.return_value = [create_client_list_straatnamen_item()]
        g = Gemeente(niscode="1", naam="test-gemeente", gateway=gateway)
        straten = g.straten
        assert len(straten) == 1
        assert straten[0].id == "1"

    def test_provincie(self, gateway):
        g = Gemeente(
            niscode="1",
            provincie_niscode="10000",
            naam="test-gemeente",
            gateway=gateway,
        )
        provincie = g.provincie
        assert provincie.naam == "Antwerpen"

    def test_gewest(self, gateway):
        g = Gemeente(
            niscode="1",
            provincie_niscode="10000",
            naam="test-gemeente",
            gateway=gateway,
        )
        gewest = g.gewest
        assert gewest.naam == "Vlaams Gewest"
        assert gewest.id == 2
        assert gewest.niscode == "2000"

    def test_naam(self, gateway, client):
        g = gateway.get_gemeente_by_niscode("57096")
        assert g.naam() == "Moeskroen"
        assert g.naam("fr") == "Mouscron"

    def test_gemeente_brussel(self, gateway, client):
        gemeente = gateway.get_gemeente_by_niscode("21004")
        assert gemeente.naam() == "Brussel"
        assert gemeente.naam("fr") == "Bruxelles"
        assert gemeente.provincie is None
        assert gemeente.provincie_niscode is None

    def test_gemeenten_brussels_gewest(self, gateway, client):
        gemeenten = gateway.list_gemeenten("4000")
        assert 19 == len(gemeenten)
        assert "21001" == gemeenten[0].niscode
        assert "Anderlecht" == gemeenten[0].naam()


class TestDeelgemeente:
    def test_gemeente(self, gateway):
        dg = Deelgemeente(
            id_="45062A",
            naam="Sint-Maria-Horebeke",
            gemeente_niscode="45062",
            gateway=gateway,
        )
        gemeente = dg.gemeente
        assert isinstance(gemeente, Gemeente)
        assert gemeente.niscode == "45062"


class TestStraat:
    def test_adressen(self, gateway, client):
        client.get_adressen.return_value = [create_client_list_adressen_item()]
        straat = Straat(id_=1, naam="straatnaam", gateway=gateway)
        adressen = straat.adressen
        assert len(adressen) == 1
        assert adressen[0].id == "200001"

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
        assert adres.huisnummer == "27"
        assert adres.busnummer == "A"

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

    def test_perceel(self, gateway, client):
        perceel_list_item = {
            "@type": "Perceel",
            "identificator": {
                "id": "https://data.vlaanderen.be/id/perceel/13013C0384-02H003",
                "objectId": "13013C0384-02H003",
            },
            "perceelStatus": "gerealiseerd",
        }
        perceel = Perceel(id_=1, gateway=gateway).from_list_response(
            perceel=perceel_list_item, gateway=gateway
        )
        assert perceel.status == "gerealiseerd"
        assert perceel.id == "13013C0384-02H003"


class TestGebouw:
    def test_gebouw(self, gateway, client):
        client.get_gebouw.return_value = create_client_get_gebouw_item()
        gebouw = Gebouw(id_=1, gateway=gateway)
        assert gebouw.status == "gerealiseerd"
        assert gebouw.geojson == {
            "polygon": {
                "coordinates": [[[140284.15277253836, 186724.7413156703]]],
                "type": "Polygon",
            }
        }

    def test_percelen(self, gateway, client):
        client.get_gebouw.return_value = create_client_get_gebouw_item()
        gebouw = Gebouw(id_=1, gateway=gateway)
        percelen = gebouw.percelen
        assert len(percelen) == 1
        assert percelen[0].id == "23052A0059-00C000"


class TestPostinfo:
    def test_get_postinfo_by_gemeentenaam(self, gateway, client):
        client.get_postinfos.return_value = create_client_get_post_infos()
        res = gateway.get_postinfo_by_gemeentenaam("brussel")
        assert res[0].status == "gerealiseerd"

    def test_get_postinfo(self, gateway, client):
        client.get_postinfo.return_value = create_client_get_post_info()
        postinfo = Postinfo("7850", gateway)
        assert postinfo.namen("nl") == ["EDINGEN", "Lettelingen", "Mark"]
        assert postinfo.id == "7850"
        assert postinfo.status == "gerealiseerd"
        postinfo_fr = Postinfo("7850", gateway)
        assert postinfo_fr.namen("fr") == ["Enghien"]
        assert postinfo_fr.id == "7850"

    def test_get_postinfo_by_postcode(self, gateway, client):
        client.get_postinfo.return_value = create_client_get_post_info()
        postinfo = gateway.get_postinfo_by_id("7850")
        assert postinfo.namen("nl") == ["EDINGEN", "Lettelingen", "Mark"]
        assert postinfo.id == "7850"
        assert postinfo.status == "gerealiseerd"
