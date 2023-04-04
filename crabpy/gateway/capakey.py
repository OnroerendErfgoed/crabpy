"""
This module contains an opionated gateway for the capakey webservice.

.. versionadded:: 0.2.0
"""

import json
import logging

import requests
from dogpile.cache import make_region

from crabpy.gateway.exception import GatewayResourceNotFoundException
from crabpy.gateway.exception import GatewayRuntimeException

log = logging.getLogger(__name__)


def capakey_rest_gateway_request(url, headers={}, params={}):
    """
    Utility function that helps making requests to the CAPAKEY REST service.

    :param string url: URL to request.
    :param dict headers: Headers to send with the URL.
    :param dict params: Parameters to send with the URL.
    :returns: Result of the call.
    """
    try:
        # calls to geoservices give a 403 if the user-agent is not set
        headers["user-agent"] = "*"
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()
        return res
    except requests.ConnectionError as ce:
        raise GatewayRuntimeException(
            "Could not execute request due to connection problems:\n%s" % repr(ce), ce
        )
    except requests.HTTPError:
        raise GatewayResourceNotFoundException()
    except requests.RequestException as re:
        raise GatewayRuntimeException(
            "Could not execute request due to:\n%s" % repr(re), re
        )


class CapakeyRestGateway:
    """
    A REST gateway to the capakey webservice.

    .. versionadded:: 0.8.0
    """

    caches = {}

    def __init__(self, **kwargs):
        self.base_url = kwargs.get("base_url", "https://geo.api.vlaanderen.be/capakey/v2")
        self.base_headers = {"Accept": "application/json"}
        cache_regions = ["permanent", "long", "short"]
        for cr in cache_regions:
            self.caches[cr] = make_region(key_mangler=str)
        if "cache_config" in kwargs:
            for cr in cache_regions:
                if ("%s.backend" % cr) in kwargs["cache_config"]:
                    log.debug("Configuring %s region on CapakeyRestGateway", cr)
                    self.caches[cr].configure_from_config(
                        kwargs["cache_config"], "%s." % cr
                    )

    @staticmethod
    def _parse_centroid(center):
        """
        Parse response center from the CapakeyRestGateway to (CenterX, CenterY)

        :param center: response center from the CapakeyRestGateway
        :return: (CenterX, CenterY)
        """
        coordinates = json.loads(center)["coordinates"]
        return coordinates[0], coordinates[1]

    @staticmethod
    def _parse_bounding_box(bounding_box):
        """
        Parse response bounding box from the CapakeyRestGateway to (MinimumX, MinimumY, MaximumX, MaximumY)

        :param bounding_box: response bounding box from the CapakeyRestGateway
        :return: (MinimumX, MinimumY, MaximumX, MaximumY)
        """
        coordinates = json.loads(bounding_box)["coordinates"]
        x_coords = [x for x, y in coordinates[0]]
        y_coords = [y for x, y in coordinates[0]]
        return min(x_coords), min(y_coords), max(x_coords), max(y_coords)

    def list_gemeenten(self, sort=1):
        """
        List all `gemeenten` in Vlaanderen.

        :param integer sort: What field to sort on.
        :rtype: A :class:`list` of :class:`Gemeente`.
        """

        def creator():
            url = self.base_url + "/municipality"
            h = self.base_headers
            p = {"orderbyCode": sort == 1}
            res = capakey_rest_gateway_request(url, h, p).json()
            return [
                Gemeente(r["municipalityCode"], r["municipalityName"])
                for r in res["municipalities"]
            ]

        if self.caches["permanent"].is_configured:
            key = "list_gemeenten_rest#%s" % sort
            gemeente = self.caches["permanent"].get_or_create(key, creator)
        else:
            gemeente = creator()
        for g in gemeente:
            g.set_gateway(self)
        return gemeente

    def get_gemeente_by_id(self, id):
        """
        Retrieve a `gemeente` by id (the NIScode).

        :rtype: :class:`Gemeente`
        """

        def creator():
            url = self.base_url + "/municipality/%s" % id
            h = self.base_headers
            p = {"geometry": "full", "srs": "31370"}
            res = capakey_rest_gateway_request(url, h, p).json()
            return Gemeente(
                res["municipalityCode"],
                res["municipalityName"],
                self._parse_centroid(res["geometry"]["center"]),
                self._parse_bounding_box(res["geometry"]["boundingBox"]),
                res["geometry"]["shape"],
            )

        if self.caches["long"].is_configured:
            key = "get_gemeente_by_id_rest#%s" % id
            gemeente = self.caches["long"].get_or_create(key, creator)
        else:
            gemeente = creator()
        gemeente.set_gateway(self)
        return gemeente

    def list_kadastrale_afdelingen(self):
        """
        List all `kadastrale afdelingen` in Flanders.

        :param integer sort: Field to sort on.
        :rtype: A :class:`list` of :class:`Afdeling`.
        """

        def creator():
            gemeentes = self.list_gemeenten()
            res = []
            for g in gemeentes:
                res += self.list_kadastrale_afdelingen_by_gemeente(g)
            return res

        if self.caches["permanent"].is_configured:
            key = "list_afdelingen_rest"
            afdelingen = self.caches["permanent"].get_or_create(key, creator)
        else:
            afdelingen = creator()
        return afdelingen

    def list_kadastrale_afdelingen_by_gemeente(self, gemeente, sort=1):
        """
        List all `kadastrale afdelingen` in a `gemeente`.

        :param gemeente: The :class:`Gemeente` for which the \
            `afdelingen` are wanted.
        :param integer sort: Field to sort on.
        :rtype: A :class:`list` of :class:`Afdeling`.
        """
        try:
            gid = gemeente.id
        except AttributeError:
            gid = gemeente
            gemeente = self.get_gemeente_by_id(gid)
        gemeente.clear_gateway()

        def creator():
            url = self.base_url + "/municipality/%s/department" % gid
            h = self.base_headers
            p = {"orderbyCode": sort == 1}
            res = capakey_rest_gateway_request(url, h, p).json()
            return [
                Afdeling(
                    id=r["departmentCode"], naam=r["departmentName"], gemeente=gemeente
                )
                for r in res["departments"]
            ]

        if self.caches["permanent"].is_configured:
            key = f"list_kadastrale_afdelingen_by_gemeente_rest#{gid}#{sort}"
            afdelingen = self.caches["permanent"].get_or_create(key, creator)
        else:
            afdelingen = creator()
        for a in afdelingen:
            a.set_gateway(self)
        return afdelingen

    def get_kadastrale_afdeling_by_id(self, aid):
        """
        Retrieve a 'kadastrale afdeling' by id.

        :param aid: An id of a `kadastrale afdeling`.
        :rtype: A :class:`Afdeling`.
        """

        def creator():
            url = self.base_url + "/department/%s" % (aid)
            h = self.base_headers
            p = {"geometry": "full", "srs": "31370"}
            res = capakey_rest_gateway_request(url, h, p).json()
            return Afdeling(
                id=res["departmentCode"],
                naam=res["departmentName"],
                gemeente=Gemeente(res["municipalityCode"], res["municipalityName"]),
                centroid=self._parse_centroid(res["geometry"]["center"]),
                bounding_box=self._parse_bounding_box(res["geometry"]["boundingBox"]),
                shape=res["geometry"]["shape"],
            )

        if self.caches["long"].is_configured:
            key = "get_kadastrale_afdeling_by_id_rest#%s" % aid
            afdeling = self.caches["long"].get_or_create(key, creator)
        else:
            afdeling = creator()
        afdeling.set_gateway(self)
        return afdeling

    def list_secties_by_afdeling(self, afdeling):
        """
        List all `secties` in a `kadastrale afdeling`.

        :param afdeling: The :class:`Afdeling` for which the `secties` are \
            wanted. Can also be the id of and `afdeling`.
        :rtype: A :class:`list` of `Sectie`.
        """
        try:
            aid = afdeling.id
            gid = afdeling.gemeente.id
        except AttributeError:
            aid = afdeling
            afdeling = self.get_kadastrale_afdeling_by_id(aid)
            gid = afdeling.gemeente.id
        afdeling.clear_gateway()

        def creator():
            url = self.base_url + f"/municipality/{gid}/department/{aid}/section"
            h = self.base_headers
            res = capakey_rest_gateway_request(url, h).json()
            return [Sectie(r["sectionCode"], afdeling) for r in res["sections"]]

        if self.caches["long"].is_configured:
            key = "list_secties_by_afdeling_rest#%s" % aid
            secties = self.caches["long"].get_or_create(key, creator)
        else:
            secties = creator()
        for s in secties:
            s.set_gateway(self)
        return secties

    def get_sectie_by_id_and_afdeling(self, id, afdeling):
        """
        Get a `sectie`.

        :param id: An id of a sectie. eg. "A"
        :param afdeling: The :class:`Afdeling` for in which the `sectie` can \
            be found. Can also be the id of and `afdeling`.
        :rtype: A :class:`Sectie`.
        """
        try:
            aid = afdeling.id
        except AttributeError:
            aid = afdeling
            afdeling = self.get_kadastrale_afdeling_by_id(aid)
        afdeling.clear_gateway()

        def creator():
            url = (
                self.base_url
                + f"/municipality/{afdeling.gemeente.id}/department/{afdeling.id}/section/{id}"
            )
            h = self.base_headers
            p = {"geometry": "full", "srs": "31370"}
            res = capakey_rest_gateway_request(url, h, p).json()
            return Sectie(
                res["sectionCode"],
                afdeling,
                self._parse_centroid(res["geometry"]["center"]),
                self._parse_bounding_box(res["geometry"]["boundingBox"]),
                res["geometry"]["shape"],
            )

        if self.caches["long"].is_configured:
            key = f"get_sectie_by_id_and_afdeling_rest#{id}#{aid}"
            sectie = self.caches["long"].get_or_create(key, creator)
        else:
            sectie = creator()
        sectie.set_gateway(self)
        return sectie

    def parse_percid(self, capakey):
        import re

        match = re.match(
            r"^([0-9]{5})([A-Z]{1})([0-9]{4})\/([0-9]{2})([A-Z\_]{1})([0-9]{3})$", capakey
        )
        if match:
            percid = (
                match.group(1)
                + "_"
                + match.group(2)
                + "_"
                + match.group(3)
                + "_"
                + match.group(5)
                + "_"
                + match.group(6)
                + "_"
                + match.group(4)
            )
            return percid
        else:
            raise ValueError("Invalid Capakey %s can't be parsed" % capakey)

    def parse_capakey(self, percid):
        import re

        match = re.match(
            r"^([0-9]{5})_([A-Z]{1})_([0-9]{4})_([A-Z\_]{1})_([0-9]{3})_([0-9]{2})$",
            percid,
        )
        if match:
            capakey = (
                match.group(1)
                + match.group(2)
                + match.group(3)
                + "/"
                + match.group(5)
                + "_"
                + match.group(6)
                + "_"
                + match.group(4)
            )
            return capakey
        else:
            raise ValueError("Invalid percid %s can't be parsed" % percid)

    def list_percelen_by_sectie(self, sectie):
        """
        List all percelen in a `sectie`.

        :param sectie: The :class:`Sectie` for which the percelen are wanted.
        :param integer sort: Field to sort on.
        :rtype: A :class:`list` of :class:`Perceel`.
        """
        sid = sectie.id
        aid = sectie.afdeling.id
        gid = sectie.afdeling.gemeente.id
        sectie.clear_gateway()

        def creator():
            url = (
                self.base_url
                + f"/municipality/{gid}/department/{aid}/section/{sid}/parcel"
            )
            h = self.base_headers
            p = {"data": "adp", "status": "actual"}
            res = capakey_rest_gateway_request(url, h, p).json()
            return [
                Perceel(
                    r["perceelnummer"],
                    sectie,
                    r["capakey"],
                    self.parse_percid(r["capakey"]),
                )
                for r in res["parcels"]
            ]

        if self.caches["short"].is_configured:
            key = f"list_percelen_by_sectie_rest#{gid}#{aid}#{sid}"
            percelen = self.caches["short"].get_or_create(key, creator)
        else:
            percelen = creator()
        for p in percelen:
            p.set_gateway(self)
        return percelen

    def get_perceel_by_id_and_sectie(self, id, sectie):
        """
        Get a `perceel`.

        :param id: An id for a `perceel`.
        :param sectie: The :class:`Sectie` that contains the perceel.
        :rtype: :class:`Perceel`
        """
        sid = sectie.id
        aid = sectie.afdeling.id
        gid = sectie.afdeling.gemeente.id
        sectie.clear_gateway()

        def creator():
            url = (
                self.base_url
                + "/municipality/{}/department/{}/section/{}/parcel/{}".format(
                    gid, aid, sid, id
                )
            )
            h = self.base_headers
            p = {"geometry": "full", "srs": "31370", "data": "adp", "status": "actual"}
            res = capakey_rest_gateway_request(url, h, p).json()
            return Perceel(
                res["perceelnummer"],
                sectie,
                res["capakey"],
                Perceel.get_percid_from_capakey(res["capakey"]),
                res["adres"],
                None,
                None,
                self._parse_centroid(res["geometry"]["center"]),
                self._parse_bounding_box(res["geometry"]["boundingBox"]),
                res["geometry"]["shape"],
            )

        if self.caches["short"].is_configured:
            key = (
                f"get_perceel_by_id_and_sectie_rest#{id}#{sectie.id}#{sectie.afdeling.id}"
            )
            perceel = self.caches["short"].get_or_create(key, creator)
        else:
            perceel = creator()
        perceel.set_gateway(self)
        return perceel

    def _get_perceel_by(self, url, cache_key):
        def creator():
            h = self.base_headers
            p = {"geometry": "full", "srs": "31370", "data": "adp", "status": "actual"}
            res = capakey_rest_gateway_request(url, h, p).json()
            return Perceel(
                res["perceelnummer"],
                Sectie(
                    res["sectionCode"],
                    Afdeling(
                        res["departmentCode"],
                        res["departmentName"],
                        Gemeente(res["municipalityCode"], res["municipalityName"]),
                    ),
                ),
                res["capakey"],
                Perceel.get_percid_from_capakey(res["capakey"]),
                res["adres"],
                None,
                None,
                self._parse_centroid(res["geometry"]["center"]),
                self._parse_bounding_box(res["geometry"]["boundingBox"]),
                res["geometry"]["shape"],
            )

        if self.caches["short"].is_configured:
            key = cache_key
            perceel = self.caches["short"].get_or_create(key, creator)
        else:
            perceel = creator()
        perceel.set_gateway(self)
        return perceel

    def get_perceel_by_capakey(self, capakey):
        """
        Get a `perceel`.

        :param capakey: An capakey for a `perceel`.
        :rtype: :class:`Perceel`
        """

        url = self.base_url + "/parcel/%s" % capakey
        cache_key = "get_perceel_by_capakey_rest#%s" % capakey
        return self._get_perceel_by(url, cache_key)

    def get_perceel_by_coordinates(self, x, y):
        """
        Get a `perceel`.

        :param capakey: An capakey for a `perceel`.
        :rtype: :class:`Perceel`
        """

        url = self.base_url + f"/parcel?x={x}&y={y}"
        cache_key = f"get_perceel_by_coordinates_rest#{x}{y}"
        return self._get_perceel_by(url, cache_key)

    def get_perceel_by_percid(self, percid):
        """
        Get a `perceel`.

        :param percid: A percid for a `perceel`.
        :rtype: :class:`Perceel`
        """
        return self.get_perceel_by_capakey(Perceel.get_capakey_from_percid(percid))


class GatewayObject:
    """
    Abstract class for all objects being returned from the Gateway.
    """

    gateway = None
    """
    The :class:`crabpy.gateway.capakey.CapakeyGateway` to use when making
    further calls to the Capakey service.
    """

    def __init__(self, **kwargs):
        if "gateway" in kwargs:
            self.set_gateway(kwargs["gateway"])

    def set_gateway(self, gateway):
        """
        :param crabpy.gateway.capakey.CapakeyGateway gateway: Gateway to use.
        """
        self.gateway = gateway

    def clear_gateway(self):
        """
        Clear the currently set CapakeyGateway.
        """
        self.gateway = None

    def check_gateway(self):
        """
        Check to see if a gateway was set on this object.
        """
        if not self.gateway:
            raise RuntimeError("There's no Gateway I can use")

    def __str__(self):
        return self.__unicode__()


def check_lazy_load_gemeente(f):
    """
    Decorator function to lazy load a :class:`Gemeente`.
    """

    def wrapper(self):
        gemeente = self
        if getattr(gemeente, "_%s" % f.__name__, None) is None:
            log.debug("Lazy loading Gemeente %d", gemeente.id)
            gemeente.check_gateway()
            g = gemeente.gateway.get_gemeente_by_id(gemeente.id)
            gemeente._naam = g._naam
            gemeente._centroid = g._centroid
            gemeente._bounding_box = g._bounding_box
        return f(self)

    return wrapper


class Gemeente(GatewayObject):
    """
    The smallest administrative unit in Belgium.
    """

    def __init__(
        self, id, naam=None, centroid=None, bounding_box=None, shape=None, **kwargs
    ):
        self.id = int(id)
        self._naam = naam
        self._centroid = centroid
        self._bounding_box = bounding_box
        self.shape = shape
        super().__init__(**kwargs)

    @property
    @check_lazy_load_gemeente
    def naam(self):
        return self._naam

    @property
    @check_lazy_load_gemeente
    def centroid(self):
        return self._centroid

    @property
    @check_lazy_load_gemeente
    def bounding_box(self):
        return self._bounding_box

    @property
    def afdelingen(self):
        self.check_gateway()
        return self.gateway.list_kadastrale_afdelingen_by_gemeente(self)

    def __unicode__(self):
        return f"{self.naam} ({self.id})"

    def __repr__(self):
        return f"Gemeente({self.id}, '{self.naam}')"


def check_lazy_load_afdeling(f):
    """
    Decorator function to lazy load a :class:`Afdeling`.
    """

    def wrapper(self):
        afdeling = self
        if getattr(afdeling, "_%s" % f.__name__, None) is None:
            log.debug("Lazy loading Afdeling %d", afdeling.id)
            afdeling.check_gateway()
            a = afdeling.gateway.get_kadastrale_afdeling_by_id(afdeling.id)
            afdeling._naam = a._naam
            afdeling._gemeente = a._gemeente
            afdeling._centroid = a._centroid
            afdeling._bounding_box = a._bounding_box
        return f(self)

    return wrapper


class Afdeling(GatewayObject):
    """
    A Cadastral Division of a :class:`Gemeente`.
    """

    def __init__(
        self,
        id,
        naam=None,
        gemeente=None,
        centroid=None,
        bounding_box=None,
        shape=None,
        **kwargs,
    ):
        self.id = int(id)
        self._naam = naam
        self._gemeente = gemeente
        self._centroid = centroid
        self._bounding_box = bounding_box
        self.shape = shape
        super().__init__(**kwargs)

    def set_gateway(self, gateway):
        """
        :param crabpy.gateway.capakey.CapakeyGateway gateway: Gateway to use.
        """
        self.gateway = gateway
        if self._gemeente is not None:
            self._gemeente.set_gateway(gateway)

    def clear_gateway(self):
        """
        Clear the currently set CapakeyGateway.
        """
        self.gateway = None
        if self._gemeente is not None:
            self._gemeente.clear_gateway()

    @property
    @check_lazy_load_afdeling
    def naam(self):
        return self._naam

    @property
    @check_lazy_load_afdeling
    def gemeente(self):
        return self._gemeente

    @property
    @check_lazy_load_afdeling
    def centroid(self):
        return self._centroid

    @property
    @check_lazy_load_afdeling
    def bounding_box(self):
        return self._bounding_box

    @property
    def secties(self):
        self.check_gateway()
        return self.gateway.list_secties_by_afdeling(self)

    def __unicode__(self):
        if self._naam is not None:
            return f"{self._naam} ({self.id})"
        else:
            return "Afdeling %s" % (self.id)

    def __repr__(self):
        if self._naam is not None:
            return f"Afdeling({self.id}, '{self._naam}')"
        else:
            return "Afdeling(%s)" % (self.id)


def check_lazy_load_sectie(f):
    """
    Decorator function to lazy load a :class:`Sectie`.
    """

    def wrapper(self):
        sectie = self
        if getattr(sectie, "_%s" % f.__name__, None) is None:
            log.debug(
                "Lazy loading Sectie %s in Afdeling %d", sectie.id, sectie.afdeling.id
            )
            sectie.check_gateway()
            s = sectie.gateway.get_sectie_by_id_and_afdeling(
                sectie.id, sectie.afdeling.id
            )
            sectie._centroid = s._centroid
            sectie._bounding_box = s._bounding_box
        return f(self)

    return wrapper


class Sectie(GatewayObject):
    """
    A subdivision of a :class:`Afdeling`.
    """

    def __init__(
        self, id, afdeling, centroid=None, bounding_box=None, shape=None, **kwargs
    ):
        self.id = id
        self.afdeling = afdeling
        self._centroid = centroid
        self._bounding_box = bounding_box
        self.shape = shape
        super().__init__(**kwargs)

    def set_gateway(self, gateway):
        """
        :param crabpy.gateway.capakey.CapakeyGateway gateway: Gateway to use.
        """
        self.gateway = gateway
        self.afdeling.set_gateway(gateway)

    def clear_gateway(self):
        """
        Clear the currently set CapakeyGateway.
        """
        self.gateway = None
        self.afdeling.clear_gateway()

    @property
    @check_lazy_load_sectie
    def centroid(self):
        return self._centroid

    @property
    @check_lazy_load_sectie
    def bounding_box(self):
        return self._bounding_box

    @property
    def percelen(self):
        self.check_gateway()
        return self.gateway.list_percelen_by_sectie(self)

    def __unicode__(self):
        return f"{self.afdeling}, Sectie {self.id}"

    def __repr__(self):
        return f"Sectie('{self.id}', {repr(self.afdeling)})"


def check_lazy_load_perceel(f):
    """
    Decorator function to lazy load a :class:`Perceel`.
    """

    def wrapper(self):
        perceel = self
        if getattr(perceel, "_%s" % f.__name__, None) is None:
            log.debug(
                "Lazy loading Perceel %s in Sectie %s in Afdeling %d",
                perceel.id,
                perceel.sectie.id,
                perceel.sectie.afdeling.id,
            )
            perceel.check_gateway()
            p = perceel.gateway.get_perceel_by_id_and_sectie(perceel.id, perceel.sectie)
            perceel._centroid = p._centroid
            perceel._bounding_box = p._bounding_box
            perceel._capatype = p._capatype
            perceel._cashkey = p._cashkey
        return f(self)

    return wrapper


class Perceel(GatewayObject):
    """
    A Cadastral Parcel.
    """

    def __init__(
        self,
        id,
        sectie,
        capakey,
        percid,
        adres=None,
        capatype=None,
        cashkey=None,
        centroid=None,
        bounding_box=None,
        shape=None,
        **kwargs,
    ):
        self.id = id
        self.sectie = sectie
        self.capakey = capakey
        self.percid = percid
        self.adres = adres
        self._capatype = capatype
        self._cashkey = cashkey
        self._centroid = centroid
        self._bounding_box = bounding_box
        self.shape = shape
        super().__init__(**kwargs)
        self._split_capakey()

    def set_gateway(self, gateway):
        """
        :param crabpy.gateway.capakey.CapakeyGateway gateway: Gateway to use.
        """
        self.gateway = gateway
        self.sectie.set_gateway(gateway)

    def clear_gateway(self):
        """
        Clear the currently set CapakeyGateway.
        """
        self.gateway = None
        self.sectie.clear_gateway()

    @staticmethod
    def get_percid_from_capakey(capakey):
        import re

        match = re.match(
            r"^([0-9]{5})([A-Z]{1})([0-9]{4})\/([0-9]{2})([A-Z\_]{1})([0-9]{3})$", capakey
        )
        if match:
            percid = (
                match.group(1)
                + "_"
                + match.group(2)
                + "_"
                + match.group(3)
                + "_"
                + match.group(5)
                + "_"
                + match.group(6)
                + "_"
                + match.group(4)
            )
            return percid
        else:
            raise ValueError("Invalid Capakey %s can't be parsed" % capakey)

    @staticmethod
    def get_capakey_from_percid(percid):
        import re

        match = re.match(
            r"^([0-9]{5})_([A-Z]{1})_([0-9]{4})_([A-Z\_]{1})_([0-9]{3})_([0-9]{2})$",
            percid,
        )
        if match:
            capakey = (
                match.group(1)
                + match.group(2)
                + match.group(3)
                + "/"
                + match.group(6)
                + match.group(4)
                + match.group(5)
            )
            return capakey
        else:
            raise ValueError("Invalid percid %s can't be parsed" % percid)

    def _split_capakey(self):
        """
        Split a capakey into more readable elements.

        Splits a capakey into it's grondnummer, bisnummer, exponent and macht.
        """
        import re

        match = re.match(
            r"^[0-9]{5}[A-Z]{1}([0-9]{4})\/([0-9]{2})([A-Z\_]{1})([0-9]{3})$",
            self.capakey,
        )
        if match:
            self.grondnummer = match.group(1)
            self.bisnummer = match.group(2)
            self.exponent = match.group(3)
            self.macht = match.group(4)
        else:
            raise ValueError("Invalid Capakey %s can't be parsed" % self.capakey)

    @property
    @check_lazy_load_perceel
    def centroid(self):
        return self._centroid

    @property
    @check_lazy_load_perceel
    def bounding_box(self):
        return self._bounding_box

    @property
    @check_lazy_load_perceel
    def capatype(self):
        return self._capatype

    @property
    @check_lazy_load_perceel
    def cashkey(self):
        return self._cashkey

    def __unicode__(self):
        return self.capakey

    def __repr__(self):
        return "Perceel('{}', {}, '{}', '{}')".format(
            self.id, repr(self.sectie), self.capakey, self.percid
        )
