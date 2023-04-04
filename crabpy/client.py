"""
This module contains utility functions for interacting with AGIV SOAP services.

.. versionadded:: 0.1.0
"""
import logging

import requests
from requests import RequestException
from suds.client import Client

log = logging.getLogger(__name__)


def crab_factory(**kwargs):
    """
    Factory that generates a CRAB client.

    A few parameters will be handled by the factory, other parameters will
    be passed on to the client.

    :param wsdl: `Optional.` Allows overriding the default CRAB wsdl url.
    :param proxy: `Optional.` A dictionary of proxy information that is passed
        to the underlying :class:`suds.client.Client`
    :rtype: :class:`suds.client.Client`
    """
    if "wsdl" in kwargs:
        wsdl = kwargs["wsdl"]
        del kwargs["wsdl"]
    else:
        wsdl = "http://crab.agiv.be/wscrab/wscrab.svc?wsdl"
    log.info("Creating CRAB client with wsdl: %s", wsdl)
    c = Client(wsdl, **kwargs)
    return c


def crab_request(client, action, *args):
    """
    Utility function that helps making requests to the CRAB service.

    :param client: A :class:`suds.client.Client` for the CRAB service.
    :param string action: Which method to call, eg. `ListGewesten`
    :returns: Result of the SOAP call.

    .. versionadded:: 0.3.0
    """
    log.debug("Calling %s on CRAB service.", action)
    return getattr(client.service, action)(*args)


class AdressenRegisterClientException(Exception):
    pass


class AdressenRegisterClient:
    def __init__(self, base_url, api_key):
        super().__init__()
        self.session = requests.Session()
        self.v1_header = {"Accept": "application/json", "x-api-key": api_key}
        self.v2_header = {"Accept": "application/ld+json", "x-api-key": api_key}
        self.base_url = base_url[:-1] if base_url.endswith("/") else base_url

    def _get_list(self, url, response_key, params=None):
        if params is None:
            params = {}
        if "limit" not in params:
            params["limit"] = 500
        result = []
        response = {"volgende": f"{self.base_url}{url}"}
        try:
            while "volgende" in response:
                response = self.session.get(
                    response["volgende"],
                    params=params,
                    headers=self.v2_header if "v2" in url else self.v1_header,
                )
                response.raise_for_status()
                response = response.json()
                result.extend(response[response_key])
        except RequestException as e:
            raise AdressenRegisterClientException from e
        return result

    def _get(self, url, params=None):
        try:
            response = self.session.get(f"{self.base_url}{url}", params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise AdressenRegisterClientException from e

    def get_gemeente(self, gemeente_id):
        return self._get(f"/v2/gemeenten/{gemeente_id}")

    def get_gemeenten(self, gemeentenaam=None, status=None):
        params = {}
        if gemeentenaam is not None:
            params["gemeentenaam"] = gemeentenaam
        if status is not None:
            params["status"] = status
        return self._get_list("/v2/gemeenten", "gemeenten", params)

    def get_postinfo(self, postinfo_id):
        return self._get(f"/v2/postinfo/{postinfo_id}")

    def get_postinfos(self, gemeentenaam=None, postnaam=None):
        params = {}
        if gemeentenaam is not None:
            params["gemeentenaam"] = gemeentenaam
        if postnaam is not None:
            params["postnaam"] = postnaam
        return self._get_list("/v2/postinfo", "postInfoObjecten", params=params)

    def get_straatnaam(self, straatnaam_id):
        return self._get(f"/v2/straatnamen/{straatnaam_id}")

    def get_straatnamen(
        self, straatnaam=None, gemeentenaam=None, niscode=None, status=None
    ):
        params = {}
        if straatnaam is not None:
            params["straatnaam"] = straatnaam
        if gemeentenaam is not None:
            params["gemeentenaam"] = gemeentenaam
        if niscode is not None:
            params["nisCode"] = niscode
        if status is not None:
            params["status"] = status
        return self._get_list("/v2/straatnamen", "straatnamen", params=params)

    def get_adres_match(
        self,
        gemeentenaam=None,
        niscode=None,
        postcode=None,
        kadaster_straatcode=None,
        rr_straatcode=None,
        straatnaam=None,
        huisnummer=None,
        index=None,
        busnummer=None,
    ):
        params = {}
        if gemeentenaam is not None:
            params["gemeentenaam"] = gemeentenaam
        if niscode is not None:
            params["niscode"] = niscode
        if postcode is not None:
            params["postcode"] = postcode
        if kadaster_straatcode is not None:
            params["kadStraatcode"] = kadaster_straatcode
        if rr_straatcode is not None:
            params["rrStraatcode"] = rr_straatcode
        if straatnaam is not None:
            params["straatnaam"] = straatnaam
        if huisnummer is not None:
            params["huisnummer"] = huisnummer
        if index is not None:
            params["index"] = index
        if busnummer is not None:
            params["busnummer"] = busnummer
        return self._get("/v1/adresmatch", params=params)

    def get_adres(self, adres_id):
        return self._get(f"/v2/adressen/{adres_id}")

    def get_adressen(
        self,
        gemeentenaam=None,
        postcode=None,
        straatnaam=None,
        homoniem_toevoeging=None,
        huisnummer=None,
        busnummer=None,
        niscode=None,
        status=None,
        straatnaamObjectId=None,
    ):
        params = {}
        if gemeentenaam is not None:
            params["gemeentenaam"] = gemeentenaam
        if postcode is not None:
            params["postcode"] = postcode
        if straatnaam is not None:
            params["straatnaam"] = straatnaam
        if homoniem_toevoeging is not None:
            params["homoniemToevoeging"] = homoniem_toevoeging
        if huisnummer is not None:
            params["huisnummer"] = huisnummer
        if busnummer is not None:
            params["busnummer"] = busnummer
        if niscode is not None:
            params["niscode"] = niscode
        if status is not None:
            params["status"] = status
        if straatnaamObjectId is not None:
            params["straatnaamObjectId"] = straatnaamObjectId
        return self._get_list("/v2/adressen", "adressen", params=params)

    def get_perceel(self, perceel_id):
        return self._get(f"/v2/percelen/{perceel_id}")

    def get_percelen(self, status=None, adresObjectId=None):
        params = {}
        if status is not None:
            params["status"] = status
        if adresObjectId is not None:
            params["adresOjbectId"] = adresObjectId
        return self._get_list("/v2/percelen", "percelen", params=params)

    def get_gebouw(self, gebouw_id):
        return self._get(f"/v2/gebouwen/{gebouw_id}")

    def get_gebouwen(self, status=None):
        params = {}
        if status is not None:
            params["status"] = status
        return self._get_list("/v2/gebouwen", "gebouwen", params=params)
