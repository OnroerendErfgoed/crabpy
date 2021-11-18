import pytest
from responses import RequestsMock

from crabpy.client import AdressenRegisterClient
from crabpy.client import (
    crab_factory,
)


@pytest.mark.skipif(
    not pytest.config.getoption("--crab-integration"),
    reason="No CRAB Integration tests required",
)
class TestCrabClient:
    def setup_method(self, method):
        self.crab = crab_factory()

    def teardown_method(self, method):
        self.crab = None

    def test_override_wsdl(self):
        wsdl = "http://crab.agiv.be/wscrab/wscrab.svc?wsdl"
        self.crab = crab_factory(wsdl=wsdl)
        assert self.crab.wsdl.url == wsdl

    def test_list_gemeenten(self):
        res = self.crab.service.ListGemeentenByGewestId(2)
        assert len(res) > 0


class TestAdressenRegisterClient:
    @pytest.fixture()
    def client(self):
        return AdressenRegisterClient("https://test-adres.be", "key")

    @pytest.fixture()
    def requests_mock(self):
        with RequestsMock() as requests_mock:
            yield requests_mock

    def test_get_gemeente(self, client, requests_mock):
        requests_mock.add(
            method=requests_mock.GET,
            url="https://test-adres.be/v1/gemeenten/123",
            json={"name": "test-gemeente"},
        )
        res = client.get_gemeente("123")
        assert res == {"name": "test-gemeente"}

    def test_get_gemeenten(self, client, requests_mock):
        requests_mock.add(
            method=requests_mock.GET,
            url="https://test-adres.be/v1/gemeenten",
            json={"gemeenten": [{"name": "test-gemeente"}]},
        )
        res = client.get_gemeenten()
        assert res == [{"name": "test-gemeente"}]

    def test_get_postinfo(self, client, requests_mock):
        requests_mock.add(
            method=requests_mock.GET,
            url="https://test-adres.be/v1/postinfo/123",
            json={"name": "test-postinfo"},
        )
        res = client.get_postinfo("123")
        assert res == {"name": "test-postinfo"}

    def test_get_postinfos(self, client, requests_mock):
        requests_mock.add(
            method=requests_mock.GET,
            url="https://test-adres.be/v1/postinfo",
            json={"postInfoObjecten": [{"name": "test-postinfo"}]},
        )
        res = client.get_postinfos()
        assert res == [{"name": "test-postinfo"}]

    def test_get_straatnaam(self, client, requests_mock):
        requests_mock.add(
            method=requests_mock.GET,
            url="https://test-adres.be/v1/straatnamen/123",
            json={"name": "test-straatnaam"},
        )
        res = client.get_straatnaam("123")
        assert res == {"name": "test-straatnaam"}

    def test_get_straatnamen(self, client, requests_mock):
        requests_mock.add(
            method=requests_mock.GET,
            url="https://test-adres.be/v1/straatnamen",
            json={"straatnamen": [{"name": "test-straatnaam"}]},
        )
        res = client.get_straatnamen()
        assert res == [{"name": "test-straatnaam"}]

    def test_get_adres(self, client, requests_mock):
        requests_mock.add(
            method=requests_mock.GET,
            url="https://test-adres.be/v1/adressen/123",
            json={"name": "test-adres"},
        )
        res = client.get_adres("123")
        assert res == {"name": "test-adres"}

    def test_get_adressen(self, client, requests_mock):
        requests_mock.add(
            method=requests_mock.GET,
            url="https://test-adres.be/v1/adressen",
            json={"adressen": [{"name": "test-adres"}]},
        )
        res = client.get_adressen()
        assert res == [{"name": "test-adres"}]

    def test_get_perceel(self, client, requests_mock):
        requests_mock.add(
            method=requests_mock.GET,
            url="https://test-adres.be/v1/percelen/123",
            json={"name": "test-perceel"},
        )
        res = client.get_perceel("123")
        assert res == {"name": "test-perceel"}

    def test_get_percelen(self, client, requests_mock):
        requests_mock.add(
            method=requests_mock.GET,
            url="https://test-adres.be/v1/percelen",
            json={"percelen": [{"name": "test-perceel"}]},
        )
        res = client.get_percelen()
        assert res == [{"name": "test-perceel"}]

    def test_get_gebouw(self, client, requests_mock):
        requests_mock.add(
            method=requests_mock.GET,
            url="https://test-adres.be/v1/gebouwen/123",
            json={"name": "test-gebouw"},
        )
        res = client.get_gebouw("123")
        assert res == {"name": "test-gebouw"}

    def test_get_gebouwen(self, client, requests_mock):
        requests_mock.add(
            method=requests_mock.GET,
            url="https://test-adres.be/v1/gebouwen",
            json={"gebouwen": [{"name": "test-gebouw"}]},
        )
        res = client.get_gebouwen()
        assert res == [{"name": "test-gebouw"}]

    def test_get_adres_match(self, client, requests_mock):
        response = {
            "adresMatches": [
                {
                    "gemeente": {
                        "objectId": "11001",
                        "detail": "https://test.be/v1/gemeenten/11001",
                        "gemeentenaam": {
                            "geografischeNaam": {
                                "spelling": "Aartselaar",
                                "taal": "nl",
                            }
                        },
                    },
                }
            ]
        }
        requests_mock.add(
            method=requests_mock.GET,
            url="https://test-adres.be/v1/adresmatch",
            json=response,
        )
        res = client.get_adres_match()
        assert res == response

    def test_list_multiple_pages(self, client, requests_mock):
        requests_mock.add(
            method=requests_mock.GET,
            url="https://test-adres.be/v1/gemeenten",
            json={
                "gemeenten": [{"name": "test-gemeente1"}],
                "volgende": "https://test-adres.be/v1/gemeenten"
            },
        )
        requests_mock.add(
            method=requests_mock.GET,
            url="https://test-adres.be/v1/gemeenten",
            json={
                "gemeenten": [{"name": "test-gemeente2"}],
            },
        )
        res = client.get_gemeenten()
        assert res == [{"name": "test-gemeente1"}, {"name": "test-gemeente2"}]
