"""
This module contains an opionated gateway for the crab webservice.

.. versionadded:: 0.3.0
"""

import json
import logging
import math
import os

from dogpile.cache import make_region
from suds import WebFault

from crabpy.client import crab_request
from crabpy.gateway.exception import GatewayResourceNotFoundException
from crabpy.gateway.exception import GatewayRuntimeException

log = logging.getLogger(__name__)


def crab_gateway_request(client, method, *args):
    """
    Utility function that helps making requests to the CRAB service.

    This is a specialised version of :func:`crabpy.client.crab_request` that
    allows adding extra functionality for the calls made by the gateway.

    :param client: A :class:`suds.client.Client` for the CRAB service.
    :param string action: Which method to call, eg. `ListGewesten`
    :returns: Result of the SOAP call.
    """
    try:
        return crab_request(client, method, *args)
    except WebFault as wf:
        err = GatewayRuntimeException(
            "Could not execute request. Message from server:\n%s"
            % wf.fault["faultstring"],
            wf,
        )
        raise err


class CrabGateway:
    """
    A gateway to the CRAB webservice.
    """

    caches = {}

    provincies = [
        (10000, "Antwerpen", 2),
        (20001, "Vlaams-Brabant", 2),
        (30000, "West-Vlaanderen", 2),
        (40000, "Oost-Vlaanderen", 2),
        (70000, "Limburg", 2),
        (20002, "Waals-Brabant", 3),
        (50000, "Henegouwen", 3),
        (60000, "Luik", 3),
        (80000, "Luxemburg", 3),
        (90000, "Namen", 3),
    ]

    def __init__(self, client, **kwargs):
        self.client = client
        cache_regions = ["permanent", "long", "short"]
        for cr in cache_regions:
            self.caches[cr] = make_region(key_mangler=str)
        if "cache_config" in kwargs:
            for cr in cache_regions:
                if ("%s.backend" % cr) in kwargs["cache_config"]:
                    log.debug("Configuring %s region on CrabGateway", cr)
                    self.caches[cr].configure_from_config(
                        kwargs["cache_config"], "%s." % cr
                    )
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        with open(os.path.join(data_dir, "deelgemeenten.json"), encoding="utf-8") as f:
            deelgemeenten_json = json.load(f)

        self.deelgemeenten = {
            dg["id"]: {
                "id": dg["id"],
                "naam": dg["naam"],
                "gemeente_niscode": int(dg["gemeente_niscode"]),
            }
            for dg in deelgemeenten_json
        }

    def list_gewesten(self, sort=1):
        """
        List all `gewesten` in Belgium.

        :param integer sort: What field to sort on.
        :rtype: A :class`list` of class: `Gewest`.
        """

        def creator():
            res = crab_gateway_request(self.client, "ListGewesten", sort)
            tmp = {}
            for r in res.GewestItem:
                if r.GewestId not in tmp:
                    tmp[r.GewestId] = {}
                tmp[r.GewestId][r.TaalCodeGewestNaam] = r.GewestNaam
            return [Gewest(k, v) for k, v in tmp.items()]

        if self.caches["permanent"].is_configured:
            key = "ListGewesten#%s" % sort
            gewesten = self.caches["permanent"].get_or_create(key, creator)
        else:
            gewesten = creator()
        for g in gewesten:
            g.set_gateway(self)
        return gewesten

    def get_gewest_by_id(self, id):
        """
        Get a `gewest` by id.

        :param integer id: The id of a `gewest`.
        :rtype: A :class:`Gewest`.
        """

        def creator():
            nl = crab_gateway_request(
                self.client, "GetGewestByGewestIdAndTaalCode", id, "nl"
            )
            fr = crab_gateway_request(
                self.client, "GetGewestByGewestIdAndTaalCode", id, "fr"
            )
            de = crab_gateway_request(
                self.client, "GetGewestByGewestIdAndTaalCode", id, "de"
            )
            if nl is None:
                raise GatewayResourceNotFoundException()
            return Gewest(
                nl.GewestId,
                {"nl": nl.GewestNaam, "fr": fr.GewestNaam, "de": de.GewestNaam},
                (nl.CenterX, nl.CenterY),
                (nl.MinimumX, nl.MinimumY, nl.MaximumX, nl.MaximumY),
            )

        if self.caches["permanent"].is_configured:
            key = "GetGewestByGewestId#%s" % id
            gewest = self.caches["long"].get_or_create(key, creator)
        else:
            gewest = creator()
        gewest.set_gateway(self)
        return gewest

    def list_provincies(self, gewest=2):
        """
        List all `provincies` in a `gewest`.

        :param gewest: The :class:`Gewest` for which the \
            `provincies` are wanted.
        :param integer sort: What field to sort on.
        :rtype: A :class:`list` of :class:`Provincie`.
        """
        try:
            gewest_id = gewest.id
        except AttributeError:
            gewest_id = gewest

        def creator():
            return [
                Provincie(p[0], p[1], Gewest(p[2]))
                for p in self.provincies
                if p[2] == gewest_id
            ]

        if self.caches["permanent"].is_configured:
            key = "ListProvinciesByGewestId#%s" % gewest_id
            provincies = self.caches["permanent"].get_or_create(key, creator)
        else:
            provincies = creator()
        for p in provincies:
            p.set_gateway(self)
        return provincies

    def get_provincie_by_id(self, niscode):
        """
        Retrieve a `provincie` by the niscode.

        :param integer niscode: The niscode of the provincie.
        :rtype: :class:`Provincie`
        """

        def creator():
            for p in self.provincies:
                if p[0] == niscode:
                    return Provincie(p[0], p[1], Gewest(p[2]))

        if self.caches["permanent"].is_configured:
            key = "GetProvincieByProvincieNiscode#%s" % niscode
            provincie = self.caches["permanent"].get_or_create(key, creator)
        else:
            provincie = creator()
        if provincie is None:
            raise GatewayResourceNotFoundException()
        provincie.set_gateway(self)
        return provincie

    def list_gemeenten_by_provincie(self, provincie):
        """
        List all `gemeenten` in a `provincie`.

        :param provincie: The :class:`Provincie` for which the \
            `gemeenten` are wanted.
        :rtype: A :class:`list` of :class:`Gemeente`.
        """
        try:
            gewest = provincie.gewest
            prov = provincie
        except AttributeError:
            prov = self.get_provincie_by_id(provincie)
            gewest = prov.gewest
        gewest.clear_gateway()

        def creator():
            gewest_gemeenten = self.list_gemeenten(gewest.id)
            return [
                Gemeente(r.id, r.naam, r.niscode, gewest)
                for r in gewest_gemeenten
                if str(r.niscode)[0] == str(prov.niscode)[0]
            ]

        if self.caches["permanent"].is_configured:
            key = "ListGemeentenByProvincieId#%s" % prov.id
            gemeente = self.caches["long"].get_or_create(key, creator)
        else:
            gemeente = creator()
        for g in gemeente:
            g.set_gateway(self)
        return gemeente

    def list_gemeenten(self, gewest=2, sort=1):
        """
        List all `gemeenten` in a `gewest`.

        :param gewest: The :class:`Gewest` for which the \
            `gemeenten` are wanted.
        :param integer sort: What field to sort on.
        :rtype: A :class:`list` of :class:`Gemeente`.
        """
        try:
            gewest_id = gewest.id
        except AttributeError:
            gewest_id = gewest
            gewest = self.get_gewest_by_id(gewest_id)
        gewest.clear_gateway()

        def creator():
            res = crab_gateway_request(
                self.client, "ListGemeentenByGewestId", gewest_id, sort
            )
            return [
                Gemeente(r.GemeenteId, r.GemeenteNaam, r.NISGemeenteCode, gewest)
                for r in res.GemeenteItem
                if r.TaalCode == r.TaalCodeGemeenteNaam
            ]

        if self.caches["permanent"].is_configured:
            key = f"ListGemeentenByGewestId#{gewest_id}#{sort}"
            gemeenten = self.caches["permanent"].get_or_create(key, creator)
        else:
            gemeenten = creator()
        for g in gemeenten:
            g.set_gateway(self)
        return gemeenten

    def get_gemeente_by_id(self, id):
        """
        Retrieve a `gemeente` by the crab id.

        :param integer id: The CRAB id of the gemeente.
        :rtype: :class:`Gemeente`
        """

        def creator():
            res = crab_gateway_request(self.client, "GetGemeenteByGemeenteId", id)
            if res is None:
                raise GatewayResourceNotFoundException()
            return Gemeente(
                res.GemeenteId,
                res.GemeenteNaam,
                res.NisGemeenteCode,
                Gewest(res.GewestId),
                res.TaalCode,
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY),
                Metadata(
                    res.BeginDatum,
                    res.BeginTijd,
                    self.get_bewerking(res.BeginBewerking),
                    self.get_organisatie(res.BeginOrganisatie),
                ),
            )

        if self.caches["long"].is_configured:
            key = "GetGemeenteByGemeenteId#%s" % id
            gemeente = self.caches["long"].get_or_create(key, creator)
        else:
            gemeente = creator()
        gemeente.set_gateway(self)
        return gemeente

    def get_gemeente_by_niscode(self, niscode):
        """
        Retrieve a `gemeente` by the NIScode.

        :param integer niscode: The NIScode of the gemeente.
        :rtype: :class:`Gemeente`
        """

        def creator():
            res = crab_gateway_request(
                self.client, "GetGemeenteByNISGemeenteCode", niscode
            )
            if res is None:
                raise GatewayResourceNotFoundException()
            return Gemeente(
                res.GemeenteId,
                res.GemeenteNaam,
                res.NisGemeenteCode,
                Gewest(res.GewestId),
                res.TaalCode,
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY),
                Metadata(
                    res.BeginDatum,
                    res.BeginTijd,
                    self.get_bewerking(res.BeginBewerking),
                    self.get_organisatie(res.BeginOrganisatie),
                ),
            )

        if self.caches["long"].is_configured:
            key = "GetGemeenteByNISGemeenteCode#%s" % niscode
            gemeente = self.caches["long"].get_or_create(key, creator)
        else:
            gemeente = creator()
        gemeente.set_gateway(self)
        return gemeente

    def list_deelgemeenten(self, gewest=2):
        """
        List all `deelgemeenten` in a `gewest`.

        :param gewest: The :class:`Gewest` for which the \
            `deelgemeenten` are wanted. Currently only Flanders is supported.
        :rtype: A :class:`list` of :class:`Deelgemeente`.
        """
        try:
            gewest_id = gewest.id
        except AttributeError:
            gewest_id = gewest

        if gewest_id != 2:
            raise ValueError("Currently only deelgemeenten in Flanders are known.")

        def creator():
            return [
                Deelgemeente(dg["id"], dg["naam"], dg["gemeente_niscode"])
                for dg in self.deelgemeenten.values()
            ]

        if self.caches["permanent"].is_configured:
            key = "ListDeelgemeentenByGewestId#%s" % gewest_id
            deelgemeenten = self.caches["permanent"].get_or_create(key, creator)
        else:
            deelgemeenten = creator()
        for dg in deelgemeenten:
            dg.set_gateway(self)
        return deelgemeenten

    def list_deelgemeenten_by_gemeente(self, gemeente):
        """
        List all `deelgemeenten` in a `gemeente`.

        :param gemeente: The :class:`Gemeente` for which the \
            `deelgemeenten` are wanted. Currently only Flanders is supported.
        :rtype: A :class:`list` of :class:`Deelgemeente`.
        """
        try:
            niscode = gemeente.niscode
        except AttributeError:
            niscode = gemeente

        def creator():
            return [
                Deelgemeente(dg["id"], dg["naam"], dg["gemeente_niscode"])
                for dg in self.deelgemeenten.values()
                if dg["gemeente_niscode"] == niscode
            ]

        if self.caches["permanent"].is_configured:
            key = "ListDeelgemeentenByGemeenteId#%s" % niscode
            deelgemeenten = self.caches["permanent"].get_or_create(key, creator)
        else:
            deelgemeenten = creator()
        for dg in deelgemeenten:
            dg.set_gateway(self)
        return deelgemeenten

    def get_deelgemeente_by_id(self, id):
        """
        Retrieve a `deelgemeente` by the id.

        :param string id: The id of the deelgemeente.
        :rtype: :class:`Deelgemeente`
        """

        def creator():
            if id in self.deelgemeenten:
                dg = self.deelgemeenten[id]
                return Deelgemeente(dg["id"], dg["naam"], dg["gemeente_niscode"])
            else:
                return None

        if self.caches["permanent"].is_configured:
            key = "GetDeelgemeenteByDeelgemeenteId#%s" % id
            deelgemeente = self.caches["permanent"].get_or_create(key, creator)
        else:
            deelgemeente = creator()
        if deelgemeente is None:
            raise GatewayResourceNotFoundException()
        deelgemeente.set_gateway(self)
        return deelgemeente

    def _list_codeobject(self, function, sort, returnclass):
        def creator():
            res = crab_gateway_request(self.client, function, sort)
            return [
                globals()[returnclass](r.Code, r.Naam, r.Definitie) for r in res.CodeItem
            ]

        if self.caches["permanent"].is_configured:
            key = function + "#%s" % (sort)
            return self.caches["permanent"].get_or_create(key, creator)
        else:
            return creator()

    def list_talen(self, sort=1):
        """
        List all `talen`.

        :rtype: A :class:`list` of :class:`Taal`
        """
        return self._list_codeobject("ListTalen", sort, "Taal")

    def list_bewerkingen(self, sort=1):
        """
        List all `bewerkingen`.

        :rtype: A :class:`list` of :class:`Bewerking`
        """
        return self._list_codeobject("ListBewerkingen", sort, "Bewerking")

    def list_organisaties(self, sort=1):
        """
        List all `organisaties`.

        :rtype: A :class:`list` of :class:`Organisatie`
        """
        return self._list_codeobject("ListOrganisaties", sort, "Organisatie")

    def list_aardsubadressen(self, sort=1):
        """
        List all `aardsubadressen`.

        :rtype: A :class:`list` of :class:`Aardsubadres`
        """
        return self._list_codeobject("ListAardSubadressen", sort, "Aardsubadres")

    def list_aardadressen(self, sort=1):
        """
        List all `aardadressen`.

        :rtype: A :class:`list` of :class:`Aardadres`
        """
        return self._list_codeobject("ListAardAdressen", sort, "Aardadres")

    def list_aardgebouwen(self, sort=1):
        """
        List all `aardgebouwen`.

        :rtype: A :class:`list` of :class:`Aardgebouw`
        """
        return self._list_codeobject("ListAardGebouwen", sort, "Aardgebouw")

    def list_aardwegobjecten(self, sort=1):
        """
        List all `aardwegobjecten`.

        :rtype: A :class:`list` of :class:`Aardwegobject`
        """
        return self._list_codeobject("ListAardWegobjecten", sort, "Aardwegobject")

    def list_aardterreinobjecten(self, sort=1):
        """
        List all `aardterreinobjecten`.

        :rtype: A :class:`list` of :class:`Aardterreinobject`
        """
        return self._list_codeobject("ListAardTerreinobjecten", sort, "Aardterreinobject")

    def list_statushuisnummers(self, sort=1):
        """
        List all `statushuisnummers`.

        :rtype: A :class:`list` of :class:`Statushuisnummer`
        """
        return self._list_codeobject("ListStatusHuisnummers", sort, "Statushuisnummer")

    def list_statussubadressen(self, sort=1):
        """
        List all `statussubadressen`.

        :rtype: A :class:`list` of :class:`Statussubadres`
        """
        return self._list_codeobject("ListStatusSubadressen", sort, "Statussubadres")

    def list_statusstraatnamen(self, sort=1):
        """
        List all `statusstraatnamen`.

        :rtype: A :class:`list` of :class:`Statusstraatnaam`
        """
        return self._list_codeobject("ListStatusStraatnamen", sort, "Statusstraatnaam")

    def list_statuswegsegmenten(self, sort=1):
        """
        List all `statuswegsegmenten`.

        :rtype: A :class:`list` of :class:`Statuswegsegment`
        """
        return self._list_codeobject("ListStatusWegsegmenten", sort, "Statuswegsegment")

    def list_geometriemethodewegsegmenten(self, sort=1):
        """
        List all `geometriemethodewegsegmenten`.

        :rtype: A :class:`list` of :class:`Geometriemethodewegsegment`
        """
        return self._list_codeobject(
            "ListGeometriemethodeWegsegmenten", sort, "Geometriemethodewegsegment"
        )

    def list_statusgebouwen(self, sort=1):
        """
        List all `statusgebouwen`.

        :rtype: A :class:`list` of :class:`Statusgebouwen`
        """
        return self._list_codeobject("ListStatusGebouwen", sort, "Statusgebouw")

    def list_geometriemethodegebouwen(self, sort=1):
        """
        List all `geometriegebouwen`.

        :rtype: A :class:`list` of :class:`Geometriegebouw`
        """
        return self._list_codeobject(
            "ListGeometriemethodeGebouwen", sort, "Geometriemethodegebouw"
        )

    def list_herkomstadresposities(self, sort=1):
        """
        List all `herkomstadresposities`.

        :rtype: A :class:`list` of :class:`Herkomstadrespositie`
        """
        return self._list_codeobject(
            "ListHerkomstAdresposities", sort, "Herkomstadrespositie"
        )

    def list_straten(self, gemeente, sort=1):
        """
        List all `straten` in a `Gemeente`.

        :param gemeente: The :class:`Gemeente` for which the \
            `straten` are wanted.
        :rtype: A :class:`list` of :class:`Straat`
        """
        try:
            id = gemeente.id
        except AttributeError:
            id = gemeente

        def creator():
            res = crab_gateway_request(
                self.client, "ListStraatnamenWithStatusByGemeenteId", id, sort
            )
            try:
                return [
                    Straat(
                        r.StraatnaamId,
                        r.StraatnaamLabel,
                        id,
                        r.StatusStraatnaam,
                        r.Straatnaam,
                        r.TaalCode,
                        r.StraatnaamTweedeTaal,
                        r.TaalCodeTweedeTaal,
                    )
                    for r in res.StraatnaamWithStatusItem
                ]
            except AttributeError:
                return []

        if self.caches["long"].is_configured:
            key = f"ListStraatnamenWithStatusByGemeenteId#{id}{sort}"
            straten = self.caches["long"].get_or_create(key, creator)
        else:
            straten = creator()
        for s in straten:
            s.set_gateway(self)
        return straten

    def get_straat_by_id(self, id):
        """
        Retrieve a `straat` by the Id.

        :param integer id: The id of the `straat`.
        :rtype: :class:`Straat`
        """

        def creator():
            res = crab_gateway_request(
                self.client, "GetStraatnaamWithStatusByStraatnaamId", id
            )
            if res is None:
                raise GatewayResourceNotFoundException()
            return Straat(
                res.StraatnaamId,
                res.StraatnaamLabel,
                res.GemeenteId,
                res.StatusStraatnaam,
                res.Straatnaam,
                res.TaalCode,
                res.StraatnaamTweedeTaal,
                res.TaalCodeTweedeTaal,
                Metadata(
                    res.BeginDatum,
                    res.BeginTijd,
                    self.get_bewerking(res.BeginBewerking),
                    self.get_organisatie(res.BeginOrganisatie),
                ),
            )

        if self.caches["long"].is_configured:
            key = "GetStraatnaamWithStatusByStraatnaamId#%s" % (id)
            straat = self.caches["long"].get_or_create(key, creator)
        else:
            straat = creator()
        straat.set_gateway(self)
        return straat

    def list_huisnummers_by_straat(self, straat, sort=1):
        """
        List all `huisnummers` in a `Straat`.

        :param straat: The :class:`Straat` for which the \
            `huisnummers` are wanted.
        :rtype: A :class: `list` of :class:`Huisnummer`
        """
        try:
            id = straat.id
        except AttributeError:
            id = straat

        def creator():
            res = crab_gateway_request(
                self.client, "ListHuisnummersWithStatusByStraatnaamId", id, sort
            )
            try:
                return [
                    Huisnummer(r.HuisnummerId, r.StatusHuisnummer, r.Huisnummer, id)
                    for r in res.HuisnummerWithStatusItem
                ]
            except AttributeError:
                return []

        if self.caches["short"].is_configured:
            key = f"ListHuisnummersWithStatusByStraatnaamId#{id}{sort}"
            huisnummers = self.caches["short"].get_or_create(key, creator)
        else:
            huisnummers = creator()
        for h in huisnummers:
            h.set_gateway(self)
        return huisnummers

    def list_huisnummers_by_perceel(self, perceel, sort=1):
        """
        List all `huisnummers` on a `Pereel`.

        Generally there will only be one, but multiples are possible.

        :param perceel: The :class:`Perceel` for which the \
            `huisnummers` are wanted.
        :rtype: A :class: `list` of :class:`Huisnummer`
        """
        try:
            id = perceel.id
        except AttributeError:
            id = perceel

        def creator():
            res = crab_gateway_request(
                self.client, "ListHuisnummersWithStatusByIdentificatorPerceel", id, sort
            )
            try:
                huisnummers = []
                for r in res.HuisnummerWithStatusItem:
                    h = self.get_huisnummer_by_id(r.HuisnummerId)
                    h.clear_gateway()
                    huisnummers.append(h)
                return huisnummers
            except AttributeError:
                return []

        if self.caches["short"].is_configured:
            key = f"ListHuisnummersWithStatusByIdentificatorPerceel#{id}{sort}"
            huisnummers = self.caches["short"].get_or_create(key, creator)
        else:
            huisnummers = creator()
        for h in huisnummers:
            h.set_gateway(self)
        return huisnummers

    def get_huisnummer_by_id(self, id):
        """
        Retrieve a `huisnummer` by the Id.

        :param integer id: the Id of the `huisnummer`
        :rtype: :class:`Huisnummer`
        """

        def creator():
            res = crab_gateway_request(
                self.client, "GetHuisnummerWithStatusByHuisnummerId", id
            )
            if res is None:
                raise GatewayResourceNotFoundException()
            return Huisnummer(
                res.HuisnummerId,
                res.StatusHuisnummer,
                res.Huisnummer,
                res.StraatnaamId,
                Metadata(
                    res.BeginDatum,
                    res.BeginTijd,
                    self.get_bewerking(res.BeginBewerking),
                    self.get_organisatie(res.BeginOrganisatie),
                ),
            )

        if self.caches["short"].is_configured:
            key = "GetHuisnummerWithStatusByHuisnummerId#%s" % (id)
            huisnummer = self.caches["short"].get_or_create(key, creator)
        else:
            huisnummer = creator()
        huisnummer.set_gateway(self)
        return huisnummer

    def get_huisnummer_by_nummer_and_straat(self, nummer, straat):
        """
        Retrieve a `huisnummer` by the `nummer` and `straat`

        :param integer nummer: The huisnummer of the 'huisnummer`
        :param straat: The :class:`Straat` in which the `huisnummer` \
            is situated.
        :rtype: A :class:`Huisnummer`
        """
        try:
            straat_id = straat.id
        except AttributeError:
            straat_id = straat

        def creator():
            res = crab_gateway_request(
                self.client, "GetHuisnummerWithStatusByHuisnummer", nummer, straat_id
            )
            if res is None:
                raise GatewayResourceNotFoundException()
            return Huisnummer(
                res.HuisnummerId,
                res.StatusHuisnummer,
                res.Huisnummer,
                res.StraatnaamId,
                Metadata(
                    res.BeginDatum,
                    res.BeginTijd,
                    self.get_bewerking(res.BeginBewerking),
                    self.get_organisatie(res.BeginOrganisatie),
                ),
            )

        if self.caches["short"].is_configured:
            key = f"GetHuisnummerWithStatusByHuisnummer#{nummer}{straat_id}"
            huisnummer = self.caches["short"].get_or_create(key, creator)
        else:
            huisnummer = creator()
        huisnummer.set_gateway(self)
        return huisnummer

    def list_postkantons_by_gemeente(self, gemeente):
        """
        List all `postkantons` in a :class:`Gemeente`

        :param gemeente: The :class:`Gemeente` for which the \
            `potkantons` are wanted.
        :rtype: A :class:`list` of :class:`Postkanton`
        """
        try:
            id = gemeente.id
        except AttributeError:
            id = gemeente

        def creator():
            res = crab_gateway_request(self.client, "ListPostkantonsByGemeenteId", id)
            try:
                return [Postkanton(r.PostkantonCode) for r in res.PostkantonItem]
            except AttributeError:
                return []

        if self.caches["long"].is_configured:
            key = "ListPostkantonsByGemeenteId#%s" % (id)
            postkantons = self.caches["long"].get_or_create(key, creator)
        else:
            postkantons = creator()
        for r in postkantons:
            r.set_gateway(self)
        return postkantons

    def get_postkanton_by_huisnummer(self, huisnummer):
        """
        Retrieve a `postkanton` by the Huisnummer.

        :param huisnummer: The :class:`Huisnummer` for which the `postkanton` \
                is wanted.
        :rtype: :class:`Postkanton`
        """
        try:
            id = huisnummer.id
        except AttributeError:
            id = huisnummer

        def creator():
            res = crab_gateway_request(self.client, "GetPostkantonByHuisnummerId", id)
            if res is None:
                raise GatewayResourceNotFoundException()
            return Postkanton(res.PostkantonCode)

        if self.caches["short"].is_configured:
            key = "GetPostkantonByHuisnummerId#%s" % (id)
            postkanton = self.caches["short"].get_or_create(key, creator)
        else:
            postkanton = creator()
        postkanton.set_gateway(self)
        return postkanton

    def get_wegobject_by_id(self, id):
        """
        Retrieve a `Wegobject` by the Id.

        :param integer id: the Id of the `Wegobject`
        :rtype: :class:`Wegobject`
        """

        def creator():
            res = crab_gateway_request(
                self.client, "GetWegobjectByIdentificatorWegobject", id
            )
            if res is None:
                raise GatewayResourceNotFoundException()
            return Wegobject(
                res.IdentificatorWegobject,
                res.AardWegobject,
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY),
                Metadata(
                    res.BeginDatum,
                    res.BeginTijd,
                    self.get_bewerking(res.BeginBewerking),
                    self.get_organisatie(res.BeginOrganisatie),
                ),
            )

        if self.caches["short"].is_configured:
            key = "GetWegobjectByIdentificatorWegobject#%s" % (id)
            wegobject = self.caches["short"].get_or_create(key, creator)
        else:
            wegobject = creator()
        wegobject.set_gateway(self)
        return wegobject

    def list_wegobjecten_by_straat(self, straat):
        """
        List all `wegobjecten` in a :class:`Straat`

        :param straat: The :class:`Straat` for which the `wegobjecten` \
                are wanted.
        :rtype: A :class:`list` of :class:`Wegobject`
        """
        try:
            id = straat.id
        except AttributeError:
            id = straat

        def creator():
            res = crab_gateway_request(self.client, "ListWegobjectenByStraatnaamId", id)
            try:
                return [
                    Wegobject(r.IdentificatorWegobject, r.AardWegobject)
                    for r in res.WegobjectItem
                ]
            except AttributeError:
                return []

        if self.caches["short"].is_configured:
            key = "ListWegobjectenByStraatnaamId#%s" % (id)
            wegobjecten = self.caches["short"].get_or_create(key, creator)
        else:
            wegobjecten = creator()
        for r in wegobjecten:
            r.set_gateway(self)
        return wegobjecten

    def get_wegsegment_by_id(self, id):
        """
        Retrieve a `wegsegment` by the Id.

        :param integer id: the Id of the `wegsegment`
        :rtype: :class:`Wegsegment`
        """

        def creator():
            res = crab_gateway_request(
                self.client, "GetWegsegmentByIdentificatorWegsegment", id
            )
            if res is None:
                raise GatewayResourceNotFoundException()
            return Wegsegment(
                res.IdentificatorWegsegment,
                res.StatusWegsegment,
                res.GeometriemethodeWegsegment,
                res.Geometrie,
                Metadata(
                    res.BeginDatum,
                    res.BeginTijd,
                    self.get_bewerking(res.BeginBewerking),
                    self.get_organisatie(res.BeginOrganisatie),
                ),
            )

        if self.caches["short"].is_configured:
            key = "GetWegsegmentByIdentificatorWegsegment#%s" % (id)
            wegsegment = self.caches["short"].get_or_create(key, creator)
        else:
            wegsegment = creator()
        wegsegment.set_gateway(self)
        return wegsegment

    def list_wegsegmenten_by_straat(self, straat):
        """
        List all `wegsegmenten` in a :class:`Straat`

        :param straat: The :class:`Straat` for which the `wegsegmenten` \
                are wanted.
        :rtype: A :class:`list` of :class:`Wegsegment`
        """
        try:
            id = straat.id
        except AttributeError:
            id = straat

        def creator():
            res = crab_gateway_request(self.client, "ListWegsegmentenByStraatnaamId", id)
            try:
                return [
                    Wegsegment(r.IdentificatorWegsegment, r.StatusWegsegment)
                    for r in res.WegsegmentItem
                ]
            except AttributeError:
                return []

        if self.caches["short"].is_configured:
            key = "ListWegsegmentenByStraatnaamId#%s" % (id)
            wegsegmenten = self.caches["short"].get_or_create(key, creator)
        else:
            wegsegmenten = creator()
        for r in wegsegmenten:
            r.set_gateway(self)
        return wegsegmenten

    def list_terreinobjecten_by_huisnummer(self, huisnummer):
        """
        List all `terreinobjecten` for a :class:`Huisnummer`

        :param huisnummer: The :class:`Huisnummer` for which the \
            `terreinobjecten` are wanted.
        :rtype: A :class:`list` of :class:`Terreinobject`
        """
        try:
            id = huisnummer.id
        except AttributeError:
            id = huisnummer

        def creator():
            res = crab_gateway_request(
                self.client, "ListTerreinobjectenByHuisnummerId", id
            )
            try:
                return [
                    Terreinobject(r.IdentificatorTerreinobject, r.AardTerreinobject)
                    for r in res.TerreinobjectItem
                ]
            except AttributeError:
                return []

        if self.caches["short"].is_configured:
            key = "ListTerreinobjectenByHuisnummerId#%s" % (id)
            terreinobjecten = self.caches["short"].get_or_create(key, creator)
        else:
            terreinobjecten = creator()
        for r in terreinobjecten:
            r.set_gateway(self)
        return terreinobjecten

    def get_terreinobject_by_id(self, id):
        """
        Retrieve a `Terreinobject` by the Id.

        :param integer id: the Id of the `Terreinobject`
        :rtype: :class:`Terreinobject`
        """

        def creator():
            res = crab_gateway_request(
                self.client, "GetTerreinobjectByIdentificatorTerreinobject", id
            )
            if res is None:
                raise GatewayResourceNotFoundException()
            return Terreinobject(
                res.IdentificatorTerreinobject,
                res.AardTerreinobject,
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY),
                Metadata(
                    res.BeginDatum,
                    res.BeginTijd,
                    self.get_bewerking(res.BeginBewerking),
                    self.get_organisatie(res.BeginOrganisatie),
                ),
            )

        if self.caches["short"].is_configured:
            key = "GetTerreinobjectByIdentificatorTerreinobject#%s" % (id)
            terreinobject = self.caches["short"].get_or_create(key, creator)
        else:
            terreinobject = creator()
        terreinobject.set_gateway(self)
        return terreinobject

    def list_percelen_by_huisnummer(self, huisnummer):
        """
        List all `percelen` for a :class:`Huisnummer`

        :param huisnummer: The :class:`Huisnummer` for which the \
            `percelen` are wanted.
        :rtype: A :class:`list` of :class:`Perceel`
        """
        try:
            id = huisnummer.id
        except AttributeError:
            id = huisnummer

        def creator():
            res = crab_gateway_request(self.client, "ListPercelenByHuisnummerId", id)
            try:
                return [Perceel(r.IdentificatorPerceel) for r in res.PerceelItem]
            except AttributeError:
                return []

        if self.caches["short"].is_configured:
            key = "ListPercelenByHuisnummerId#%s" % (id)
            percelen = self.caches["short"].get_or_create(key, creator)
        else:
            percelen = creator()
        for r in percelen:
            r.set_gateway(self)
        return percelen

    def get_perceel_by_id(self, id):
        """
        Retrieve a `Perceel` by the Id.

        :param string id: the Id of the `Perceel`
        :rtype: :class:`Perceel`
        """

        def creator():
            res = crab_gateway_request(
                self.client, "GetPerceelByIdentificatorPerceel", id
            )
            if res is None:
                raise GatewayResourceNotFoundException()
            return Perceel(
                res.IdentificatorPerceel,
                (res.CenterX, res.CenterY),
                Metadata(
                    res.BeginDatum,
                    res.BeginTijd,
                    self.get_bewerking(res.BeginBewerking),
                    self.get_organisatie(res.BeginOrganisatie),
                ),
            )

        if self.caches["short"].is_configured:
            key = "GetPerceelByIdentificatorPerceel#%s" % (id)
            perceel = self.caches["short"].get_or_create(key, creator)
        else:
            perceel = creator()
        perceel.set_gateway(self)
        return perceel

    def list_gebouwen_by_huisnummer(self, huisnummer):
        """
        List all `gebouwen` for a :class:`Huisnummer`.

        :param huisnummer: The :class:`Huisnummer` for which the \
            `gebouwen` are wanted.
        :rtype: A :class:`list` of :class:`Gebouw`
        """
        try:
            id = huisnummer.id
        except AttributeError:
            id = huisnummer

        def creator():
            res = crab_gateway_request(self.client, "ListGebouwenByHuisnummerId", id)
            try:
                return [
                    Gebouw(r.IdentificatorGebouw, r.AardGebouw, r.StatusGebouw)
                    for r in res.GebouwItem
                ]
            except AttributeError:
                return []

        if self.caches["short"].is_configured:
            key = "ListGebouwenByHuisnummerId#%s" % (id)
            gebouwen = self.caches["short"].get_or_create(key, creator)
        else:
            gebouwen = creator()
        for r in gebouwen:
            r.set_gateway(self)
        return gebouwen

    def get_gebouw_by_id(self, id):
        """
        Retrieve a `Gebouw` by the Id.

        :param integer id: the Id of the `Gebouw`
        :rtype: :class:`Gebouw`
        """

        def creator():
            res = crab_gateway_request(self.client, "GetGebouwByIdentificatorGebouw", id)
            if res is None:
                raise GatewayResourceNotFoundException()
            return Gebouw(
                res.IdentificatorGebouw,
                res.AardGebouw,
                res.StatusGebouw,
                res.GeometriemethodeGebouw,
                res.Geometrie,
                Metadata(
                    res.BeginDatum,
                    res.BeginTijd,
                    self.get_bewerking(res.BeginBewerking),
                    self.get_organisatie(res.BeginOrganisatie),
                ),
            )

        if self.caches["short"].is_configured:
            key = "GetGebouwByIdentificatorGebouw#%s" % (id)
            gebouw = self.caches["short"].get_or_create(key, creator)
        else:
            gebouw = creator()
        gebouw.set_gateway(self)
        return gebouw

    def get_bewerking(self, res):
        r = self.list_bewerkingen()
        for item in r:
            if int(item.id) == int(res):
                return item

    def get_organisatie(self, res):
        r = self.list_organisaties()
        for item in r:
            if int(item.id) == int(res):
                return item

    def list_subadressen_by_huisnummer(self, huisnummer):
        """
        List all `subadressen` for a :class:`Huisnummer`.

        :param huisnummer: The :class:`Huisnummer` for which the \
            `subadressen` are wanted. OR A huisnummer id.
        :rtype: A :class:`list` of :class:`Gebouw`
        """
        try:
            id = huisnummer.id
        except AttributeError:
            id = huisnummer

        def creator():
            res = crab_gateway_request(
                self.client, "ListSubadressenWithStatusByHuisnummerId", id
            )
            try:
                return [
                    Subadres(r.SubadresId, r.Subadres, r.StatusSubadres)
                    for r in res.SubadresWithStatusItem
                ]
            except AttributeError:
                return []

        if self.caches["short"].is_configured:
            key = "ListSubadressenWithStatusByHuisnummerId#%s" % (id)
            subadressen = self.caches["short"].get_or_create(key, creator)
        else:
            subadressen = creator()
        for s in subadressen:
            s.set_gateway(self)
        return subadressen

    def get_subadres_by_id(self, id):
        """
        Retrieve a `Subadres` by the Id.

        :param integer id: the Id of the `Subadres`
        :rtype: :class:`Subadres`
        """

        def creator():
            res = crab_gateway_request(
                self.client, "GetSubadresWithStatusBySubadresId", id
            )
            if res is None:
                raise GatewayResourceNotFoundException()
            return Subadres(
                res.SubadresId,
                res.Subadres,
                res.StatusSubadres,
                res.HuisnummerId,
                res.AardSubadres,
                Metadata(
                    res.BeginDatum,
                    res.BeginTijd,
                    self.get_bewerking(res.BeginBewerking),
                    self.get_organisatie(res.BeginOrganisatie),
                ),
            )

        if self.caches["short"].is_configured:
            key = "GetSubadresWithStatusBySubadresId#%s" % (id)
            subadres = self.caches["short"].get_or_create(key, creator)
        else:
            subadres = creator()
        subadres.set_gateway(self)
        return subadres

    def list_adresposities_by_huisnummer(self, huisnummer):
        """
        List all `adresposities` for a :class:`Huisnummer`.

        :param huisnummer: The :class:`Huisnummer` for which the \
            `adresposities` are wanted. OR A huisnummer id.
        :rtype: A :class:`list` of :class:`Adrespositie`
        """
        try:
            id = huisnummer.id
        except AttributeError:
            id = huisnummer

        def creator():
            res = crab_gateway_request(self.client, "ListAdrespositiesByHuisnummerId", id)
            try:
                return [
                    Adrespositie(r.AdrespositieId, r.HerkomstAdrespositie)
                    for r in res.AdrespositieItem
                ]
            except AttributeError:
                return []

        if self.caches["short"].is_configured:
            key = "ListAdrespositiesByHuisnummerId#%s" % (id)
            adresposities = self.caches["short"].get_or_create(key, creator)
        else:
            adresposities = creator()
        for a in adresposities:
            a.set_gateway(self)
        return adresposities

    def list_adresposities_by_nummer_and_straat(self, nummer, straat):
        """
        List all `adresposities` for a huisnummer and a :class:`Straat`.

        :param nummer: A string representing a certain huisnummer.
        :param straat: The :class:`Straat` for which the \
            `adresposities` are wanted. OR A straat id.
        :rtype: A :class:`list` of :class:`Adrespositie`
        """
        try:
            sid = straat.id
        except AttributeError:
            sid = straat

        def creator():
            res = crab_gateway_request(
                self.client, "ListAdrespositiesByHuisnummer", nummer, sid
            )
            try:
                return [
                    Adrespositie(r.AdrespositieId, r.HerkomstAdrespositie)
                    for r in res.AdrespositieItem
                ]
            except AttributeError:
                return []

        if self.caches["short"].is_configured:
            key = f"ListAdrespositiesByHuisnummer#{nummer}{sid}"
            adresposities = self.caches["short"].get_or_create(key, creator)
        else:
            adresposities = creator()
        for a in adresposities:
            a.set_gateway(self)
        return adresposities

    def list_adresposities_by_subadres(self, subadres):
        """
        List all `adresposities` for a :class:`Subadres`.

        :param subadres: The :class:`Subadres` for which the \
            `adresposities` are wanted. OR A subadres id.
        :rtype: A :class:`list` of :class:`Adrespositie`
        """
        try:
            id = subadres.id
        except AttributeError:
            id = subadres

        def creator():
            res = crab_gateway_request(self.client, "ListAdrespositiesBySubadresId", id)
            try:
                return [
                    Adrespositie(r.AdrespositieId, r.HerkomstAdrespositie)
                    for r in res.AdrespositieItem
                ]
            except AttributeError:
                return []

        if self.caches["short"].is_configured:
            key = "ListAdrespositiesBySubadresId#%s" % (id)
            adresposities = self.caches["short"].get_or_create(key, creator)
        else:
            adresposities = creator()
        for a in adresposities:
            a.set_gateway(self)
        return adresposities

    def list_adresposities_by_subadres_and_huisnummer(self, subadres, huisnummer):
        """
        List all `adresposities` for a subadres and a :class:`Huisnummer`.

        :param subadres: A string representing a certain subadres.
        :param huisnummer: The :class:`Huisnummer` for which the \
            `adresposities` are wanted. OR A huisnummer id.
        :rtype: A :class:`list` of :class:`Adrespositie`
        """
        try:
            hid = huisnummer.id
        except AttributeError:
            hid = huisnummer

        def creator():
            res = crab_gateway_request(
                self.client, "ListAdrespositiesBySubadres", subadres, hid
            )
            try:
                return [
                    Adrespositie(r.AdrespositieId, r.HerkomstAdrespositie)
                    for r in res.AdrespositieItem
                ]
            except AttributeError:
                return []

        if self.caches["short"].is_configured:
            key = f"ListAdrespositiesBySubadres#{subadres}{hid}"
            adresposities = self.caches["short"].get_or_create(key, creator)
        else:
            adresposities = creator()
        for a in adresposities:
            a.set_gateway(self)
        return adresposities

    def get_adrespositie_by_id(self, id):
        """
        Retrieve a `Adrespositie` by the Id.

        :param integer id: the Id of the `Adrespositie`
        :rtype: :class:`Adrespositie`
        """

        def creator():
            res = crab_gateway_request(self.client, "GetAdrespositieByAdrespositieId", id)
            if res is None:
                raise GatewayResourceNotFoundException()
            return Adrespositie(
                res.AdrespositieId,
                res.HerkomstAdrespositie,
                res.Geometrie,
                res.AardAdres,
                Metadata(
                    res.BeginDatum,
                    res.BeginTijd,
                    self.get_bewerking(res.BeginBewerking),
                    self.get_organisatie(res.BeginOrganisatie),
                ),
            )

        if self.caches["short"].is_configured:
            key = "GetAdrespositieByAdrespositieId#%s" % (id)
            adrespositie = self.caches["short"].get_or_create(key, creator)
        else:
            adrespositie = creator()
        adrespositie.set_gateway(self)
        return adrespositie

    def get_postadres_by_huisnummer(self, huisnummer):
        """
        Get the `postadres` for a :class:`Huisnummer`.

        :param huisnummer: The :class:`Huisnummer` for which the \
            `postadres` is wanted. OR A huisnummer id.
        :rtype: A :class:`str`.
        """
        try:
            id = huisnummer.id
        except AttributeError:
            id = huisnummer

        def creator():
            res = crab_gateway_request(self.client, "GetPostadresByHuisnummerId", id)
            if res is None:
                raise GatewayResourceNotFoundException()
            return res.Postadres

        if self.caches["short"].is_configured:
            key = "GetPostadresByHuisnummerId#%s" % (id)
            postadres = self.caches["short"].get_or_create(key, creator)
        else:
            postadres = creator()
        return postadres

    def get_postadres_by_subadres(self, subadres):
        """
        Get the `postadres` for a :class:`Subadres`.

        :param subadres: The :class:`Subadres` for which the \
            `postadres` is wanted. OR A subadres id.
        :rtype: A :class:`str`.
        """
        try:
            id = subadres.id
        except AttributeError:
            id = subadres

        def creator():
            res = crab_gateway_request(self.client, "GetPostadresBySubadresId", id)
            if res is None:
                raise GatewayResourceNotFoundException()
            return res.Postadres

        if self.caches["short"].is_configured:
            key = "GetPostadresBySubadresId#%s" % (id)
            postadres = self.caches["short"].get_or_create(key, creator)
        else:
            postadres = creator()
        return postadres


class GatewayObject:
    """
    Abstract class for objects that are able to use a
    :class:`crabpy.Gateway.CrabGateway` to find further information.
    """

    gateway = None
    """
    The :class:`crabpy.gateway.crab.CrabGateway` to use when making
    further calls to the CRAB service.
    """

    def __init__(self, **kwargs):
        if "gateway" in kwargs:
            self.set_gateway(kwargs["gateway"])

    def set_gateway(self, gateway):
        """
        :param crabpy.gateway.crab.CrabGateway gateway: Gateway to use.
        """
        self.gateway = gateway

    def clear_gateway(self):
        """
        Clear the currently set CrabGateway.
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


def check_lazy_load_gewest(f):
    """
    Decorator function to lazy load a :class:`Gewest`.
    """

    def wrapper(self):
        gewest = self
        attribute = "namen" if f.__name__ == "naam" else f.__name__
        if getattr(gewest, "_%s" % attribute, None) is None:
            log.debug("Lazy loading Gewest %d", gewest.id)
            gewest.check_gateway()
            g = gewest.gateway.get_gewest_by_id(gewest.id)
            gewest._namen = g._namen
            gewest._centroid = g._centroid
            gewest._bounding_box = g._bounding_box
        return f(self)

    return wrapper


class Gewest(GatewayObject):
    """
    A large administrative unit in Belgium.

    Belgium consists of 3 `gewesten`. Together they form the entire territory
    of the country.
    """

    def __init__(self, id, namen=None, centroid=None, bounding_box=None, **kwargs):
        self.id = int(id)
        self._namen = namen
        self._centroid = centroid
        self._bounding_box = bounding_box
        super().__init__(**kwargs)

    @property
    @check_lazy_load_gewest
    def naam(self):
        return self._namen["nl"]

    @property
    @check_lazy_load_gewest
    def centroid(self):
        return self._centroid

    @property
    @check_lazy_load_gewest
    def bounding_box(self):
        return self._bounding_box

    @property
    def provincies(self):
        return self.gateway.list_provincies(self.id)

    @property
    def gemeenten(self):
        return self.gateway.list_gemeenten(self.id)

    def __unicode__(self):
        if self._namen is not None:
            return f"{self.naam} ({self.id})"
        else:
            return "Gewest %s" % (self.id)

    def __repr__(self):
        return "Gewest(%s)" % (self.id)


class Provincie(GatewayObject):
    """
    The largest administrative unit within a :class:`Gewest`.

    .. versionadded:: 0.4.0
    """

    def __init__(self, niscode, naam, gewest, **kwargs):
        self.id = self.niscode = int(niscode)
        self.naam = naam
        self.gewest = gewest

    def set_gateway(self, gateway):
        """
        :param crabpy.gateway.crab.CrabGateway gateway: Gateway to use.
        """
        self.gateway = gateway
        self.gewest.gateway = gateway

    def clear_gateway(self):
        """
        Clear the currently set CrabGateway.
        """
        self.gateway = None
        self.gewest.clear_gateway()

    @property
    def gemeenten(self):
        self.check_gateway()
        return self.gateway.list_gemeenten_by_provincie(self.niscode)

    def __unicode__(self):
        return f"{self.naam} ({self.niscode})"

    def __repr__(self):
        return f"Provincie({self.niscode}, '{self.naam}', Gewest({self.gewest.id}))"


def check_lazy_load_gemeente(f):
    """
    Decorator function to lazy load a :class:`Gemeente`.
    """

    def wrapper(*args):
        gemeente = args[0]
        if (
            gemeente._centroid is None
            or gemeente._bounding_box is None
            or gemeente._taal_id is None
            or gemeente._metadata is None
        ):
            log.debug("Lazy loading Gemeente %d", gemeente.id)
            gemeente.check_gateway()
            g = gemeente.gateway.get_gemeente_by_id(gemeente.id)
            gemeente._taal_id = g._taal_id
            gemeente._centroid = g._centroid
            gemeente._bounding_box = g._bounding_box
            gemeente._metadata = g._metadata
        return f(*args)

    return wrapper


class Gemeente(GatewayObject):
    """
    The smallest administrative unit in Belgium.
    """

    def __init__(
        self,
        id,
        naam,
        niscode,
        gewest,
        taal=None,
        centroid=None,
        bounding_box=None,
        metadata=None,
        **kwargs,
    ):
        self.id = int(id)
        self.naam = naam
        self.niscode = niscode
        self.gewest = gewest
        try:
            self._taal_id = taal.id
            self._taal = taal
        except AttributeError:
            self._taal_id = taal
            self._taal = None
        self._centroid = centroid
        self._bounding_box = bounding_box
        self._metadata = metadata
        super().__init__(**kwargs)

    def set_gateway(self, gateway):
        """
        :param crabpy.gateway.crab.CrabGateway gateway: Gateway to use.
        """
        self.gateway = gateway
        self.gewest.set_gateway(gateway)

    def clear_gateway(self):
        """
        Clear the currently set CrabGateway.
        """
        self.gateway = None
        self.gewest.clear_gateway()

    @property
    @check_lazy_load_gemeente
    def taal(self):
        if self._taal is None:
            talen = self.gateway.list_talen()
            for taal in talen:
                if taal.id == self._taal_id:
                    self._taal = taal
        return self._taal

    @property
    @check_lazy_load_gemeente
    def centroid(self):
        return self._centroid

    @property
    @check_lazy_load_gemeente
    def bounding_box(self):
        return self._bounding_box

    @property
    @check_lazy_load_gemeente
    def metadata(self):
        return self._metadata

    @property
    def straten(self):
        self.check_gateway()
        return self.gateway.list_straten(self)

    @property
    def postkantons(self):
        self.check_gateway()
        return self.gateway.list_postkantons_by_gemeente(self.id)

    @property
    def provincie(self):
        self.check_gateway()
        provincies = self.gateway.list_provincies(self.gewest)
        for p in provincies:
            if math.floor(self.niscode / 10000) == math.floor(p.niscode / 10000):
                return p

    def __unicode__(self):
        return f"{self.naam} ({self.id})"

    def __repr__(self):
        return f"Gemeente({self.id}, '{self.naam}', {self.niscode})"


class Deelgemeente(GatewayObject):
    """
    A subdivision of a :class:`Gemeente`.

    .. versionadded:: 0.7.0
    """

    def __init__(self, id, naam, gemeente_niscode, **kwargs):
        self.id = id
        self.naam = naam
        self.gemeente_niscode = gemeente_niscode

    def set_gateway(self, gateway):
        """
        :param crabpy.gateway.crab.CrabGateway gateway: Gateway to use.
        """
        self.gateway = gateway

    def clear_gateway(self):
        """
        Clear the currently set CrabGateway.
        """
        self.gateway = None

    @property
    def gemeente(self):
        return self.gateway.get_gemeente_by_niscode(self.gemeente_niscode)

    def __unicode__(self):
        return f"{self.naam} ({self.id})"

    def __repr__(self):
        return f"Deelgemeente('{self.id}', '{self.naam}', {self.gemeente_niscode})"


class Codelijst(GatewayObject):
    def __init__(self, id, naam, definitie, **kwargs):
        self.id = id
        self.naam = naam
        self.definitie = definitie
        super().__init__(**kwargs)

    def __unicode__(self):
        return self.naam


class Taal(Codelijst):
    """
    A language.
    """

    def __repr__(self):
        return f"Taal('{self.id}', '{self.naam}', '{self.definitie}')"


class Bewerking(Codelijst):
    """
    An edit.
    """

    def __repr__(self):
        return f"Bewerking({self.id}, '{self.naam}', '{self.definitie}')"


class Organisatie(Codelijst):
    """
    An organisation that played a role in the genessis of an object.
    """

    def __repr__(self):
        return f"Organisatie({self.id}, '{self.naam}', '{self.definitie}')"


class Aardsubadres(Codelijst):
    """
    The nature of a subaddress.
    """

    def __repr__(self):
        return f"Aardsubadres({self.id}, '{self.naam}', '{self.definitie}')"


class Aardadres(Codelijst):
    """
    The nature of an address.
    """

    def __repr__(self):
        return f"Aardadres({self.id}, '{self.naam}', '{self.definitie}')"


class Aardgebouw(Codelijst):
    """
    The nature of a building.
    """

    def __repr__(self):
        return f"Aardgebouw({self.id}, '{self.naam}', '{self.definitie}')"


class Aardwegobject(Codelijst):
    """
    The nature of a `wegobject`.
    """

    def __repr__(self):
        return f"Aardwegobject({self.id}, '{self.naam}', '{self.definitie}')"


class Aardterreinobject(Codelijst):
    """
    The nature of a `terreinobject`.
    """

    def __repr__(self):
        return f"Aardterreinobject({self.id}, '{self.naam}', '{self.definitie}')"


class Statushuisnummer(Codelijst):
    """
    The current state of a `huisnummer`.
    """

    def __repr__(self):
        return f"Statushuisnummer({self.id}, '{self.naam}', '{self.definitie}')"


class Statussubadres(Codelijst):
    """
    The current state of a `subadres`.
    """

    def __repr__(self):
        return f"Statussubadres({self.id}, '{self.naam}', '{self.definitie}')"


class Statusstraatnaam(Codelijst):
    """
    The current state of a `straatnaam`.
    """

    def __repr__(self):
        return f"Statusstraatnaam({self.id}, '{self.naam}', '{self.definitie}')"


class Statuswegsegment(Codelijst):
    """
    The current state of a `wegsegment`.
    """

    def __repr__(self):
        return f"Statuswegsegment({self.id}, '{self.naam}', '{self.definitie}')"


class Geometriemethodewegsegment(Codelijst):
    """
    The geometry method of a :class:`Wegsegment`.
    """

    def __repr__(self):
        return f"Geometriemethodewegsegment({self.id}, '{self.naam}', '{self.definitie}')"


class Statusgebouw(Codelijst):
    """
    The current state of a :class:`Gebouw`.
    """

    def __repr__(self):
        return f"Statusgebouw({self.id}, '{self.naam}', '{self.definitie}')"


class Geometriemethodegebouw(Codelijst):
    """
    The geometry method of a :class:`Gebouw`.
    """

    def __repr__(self):
        return f"Geometriemethodegebouw({self.id}, '{self.naam}', '{self.definitie}')"


class Herkomstadrespositie(Codelijst):
    """
    The origin of an Adressposition.
    """

    def __repr__(self):
        return f"Herkomstadrespositie({self.id}, '{self.naam}', '{self.definitie}')"


def check_lazy_load_straat(f):
    """
    Decorator function to lazy load a :class:`Straat`.
    """

    def wrapper(*args):
        straat = args[0]
        if straat._metadata is None:
            log.debug("Lazy loading Straat %d", straat.id)
            straat.check_gateway()
            s = straat.gateway.get_straat_by_id(straat.id)
            straat._metadata = s._metadata
        return f(*args)

    return wrapper


class Straat(GatewayObject):
    """
    A street.

    A street object is always located in one and exactly one :class:`Gemeente`.
    """

    def __init__(
        self,
        id,
        label,
        gemeente_id,
        status,
        straatnaam,
        taalcode,
        straatnaam2,
        taalcode2,
        metadata=None,
        **kwargs,
    ):
        self.id = id
        self.label = label
        try:
            self.status_id = status.id
            self._status = status
        except Exception:
            self.status_id = status
            self._status = None
        self._namen = ((straatnaam, taalcode), (straatnaam2, taalcode2))
        self.gemeente_id = gemeente_id
        self._metadata = metadata
        super().__init__(**kwargs)

    @property
    def namen(self):
        return self._namen

    @property
    def gemeente(self):
        return self.gateway.get_gemeente_by_id(self.gemeente_id)

    @property
    def status(self):
        if self._status is None:
            res = self.gateway.list_statusstraatnamen()
            for status in res:
                if int(status.id) == int(self.status_id):
                    self._status = status
        return self._status

    @property
    @check_lazy_load_straat
    def metadata(self):
        return self._metadata

    @property
    def huisnummers(self):
        self.check_gateway()
        return self.gateway.list_huisnummers_by_straat(self)

    @property
    @check_lazy_load_straat
    def taal(self):
        return self.gemeente.taal

    @property
    def wegobjecten(self):
        self.check_gateway()
        return self.gateway.list_wegobjecten_by_straat(self)

    @property
    def wegsegmenten(self):
        self.check_gateway()
        return self.gateway.list_wegsegmenten_by_straat(self)

    @property
    def bounding_box(self):
        weg = [x.geometrie for x in self.wegsegmenten]
        if weg == []:
            return None
        x = []
        y = []
        for a in weg:
            a = a.replace("LINESTRING (", "").replace(")", "")
            list = a.split(",")
            for z in list:
                temp = z.split()
                x.append(float(temp[0]))
                y.append(float(temp[1]))
        return [min(x), min(y), max(x), max(y)]

    def __unicode__(self):
        return f"{self.label} ({self.id})"

    def __repr__(self):
        return f"Straat({self.id}, '{self.label}', {self.gemeente_id}, {self.status_id})"


def check_lazy_load_huisnummer(f):
    """
    Decorator function to lazy load a :class:`Huisnummer`.
    """

    def wrapper(*args):
        huisnummer = args[0]
        if huisnummer._metadata is None:
            log.debug("Lazy loading Huisnummer %d", huisnummer.id)
            huisnummer.check_gateway()
            h = huisnummer.gateway.get_huisnummer_by_id(huisnummer.id)
            huisnummer._metadata = h._metadata
        return f(*args)

    return wrapper


class Huisnummer(GatewayObject):
    """
    A house number.

    This is mainly a combination of a street and a house number.
    """

    def __init__(self, id, status, huisnummer, straat_id, metadata=None, **kwargs):
        self.id = int(id)
        try:
            self.status_id = status.id
            self._status = status
        except AttributeError:
            self.status_id = status
            self._status = None
        self.huisnummer = huisnummer
        self.straat_id = straat_id
        self._metadata = metadata
        super().__init__(**kwargs)

    @property
    def straat(self):
        self.check_gateway()
        return self.gateway.get_straat_by_id(self.straat_id)

    @property
    @check_lazy_load_huisnummer
    def metadata(self):
        return self._metadata

    @property
    def status(self):
        if self._status is None:
            res = self.gateway.list_statushuisnummers()
            for status in res:
                if int(status.id) == int(self.status_id):
                    self._status = status
        return self._status

    @property
    def postkanton(self):
        self.check_gateway()
        return self.gateway.get_postkanton_by_huisnummer(self.id)

    @property
    def terreinobjecten(self):
        return self.gateway.list_terreinobjecten_by_huisnummer(self.id)

    @property
    def percelen(self):
        return self.gateway.list_percelen_by_huisnummer(self.id)

    @property
    def bounding_box(self):
        per = [x.bounding_box for x in self.terreinobjecten]
        if per == []:
            return None
        mini = min(per)
        maxi = max(per)
        return [mini[0], mini[1], maxi[0], maxi[1]]

    @property
    def postadres(self):
        self.check_gateway()
        return self.gateway.get_postadres_by_huisnummer(self.id)

    @property
    def gebouwen(self):
        self.check_gateway()
        return self.gateway.list_gebouwen_by_huisnummer(self.id)

    @property
    def subadressen(self):
        self.check_gateway()
        return self.gateway.list_subadressen_by_huisnummer(self.id)

    @property
    def adresposities(self):
        self.check_gateway()
        return self.gateway.list_adresposities_by_huisnummer(self.id)

    def __unicode__(self):
        return f"{self.huisnummer} ({self.id})"

    def __repr__(self):
        return f"Huisnummer({self.id}, {self.status_id}, '{self.huisnummer}', {self.straat_id})"


class Postkanton(GatewayObject):
    """
    A postal code.

    Eg. postal code `9000` for the city of Ghent.
    """

    def __init__(self, id, **kwargs):
        self.id = int(id)
        super().__init__(**kwargs)

    def __unicode__(self):
        return "Postkanton %s" % (self.id)

    def __repr__(self):
        return "Postkanton(%s)" % (self.id)


def check_lazy_load_wegobject(f):
    """
    Decorator function to lazy load a :class:`Wegobject`.
    """

    def wrapper(*args):
        wegobject = args[0]
        if (
            wegobject._centroid is None
            or wegobject._bounding_box is None
            or wegobject._metadata is None
        ):
            log.debug("Lazy loading Wegobject %d", wegobject.id)
            wegobject.check_gateway()
            w = wegobject.gateway.get_wegobject_by_id(wegobject.id)
            wegobject._centroid = w._centroid
            wegobject._bounding_box = w._bounding_box
            wegobject._metadata = w._metadata
        return f(*args)

    return wrapper


class Wegobject(GatewayObject):
    def __init__(
        self, id, aard, centroid=None, bounding_box=None, metadata=None, **kwargs
    ):
        self.id = id
        try:
            self.aard_id = aard.id
            self._aard = aard
        except AttributeError:
            self.aard_id = aard
            self._aard = None
        self._centroid = centroid
        self._bounding_box = bounding_box
        self._metadata = metadata
        super().__init__(**kwargs)

    @property
    def aard(self):
        if self._aard is None:
            res = self.gateway.list_aardwegobjecten()
            for aard in res:
                if int(aard.id) == int(self.aard_id):
                    self._aard = aard
        return self._aard

    @property
    @check_lazy_load_wegobject
    def centroid(self):
        return self._centroid

    @property
    @check_lazy_load_wegobject
    def bounding_box(self):
        return self._bounding_box

    @property
    @check_lazy_load_wegobject
    def metadata(self):
        return self._metadata

    def __unicode__(self):
        return "Wegobject %s" % (self.id)

    def __repr__(self):
        return "Wegobject(%s)" % (self.id)


def check_lazy_load_wegsegment(f):
    """
    Decorator function to lazy load a :class:`Wegsegment`.
    """

    def wrapper(*args):
        wegsegment = args[0]
        if (
            wegsegment._methode_id is None
            or wegsegment._geometrie is None
            or wegsegment._metadata is None
        ):
            log.debug("Lazy loading Wegsegment %d", wegsegment.id)
            wegsegment.check_gateway()
            w = wegsegment.gateway.get_wegsegment_by_id(wegsegment.id)
            wegsegment._methode_id = w._methode_id
            wegsegment._geometrie = w._geometrie
            wegsegment._metadata = w._metadata
        return f(*args)

    return wrapper


class Wegsegment(GatewayObject):
    def __init__(self, id, status, methode=None, geometrie=None, metadata=None, **kwargs):
        self.id = id
        try:
            self.status_id = status.id
            self._status = status
        except Exception:
            self.status_id = status
            self._status = None
        try:
            self._methode_id = methode.id
            self._methode = methode
        except Exception:
            self._methode_id = methode
            self._methode = None
        self._geometrie = geometrie
        self._metadata = metadata
        super().__init__(**kwargs)

    @property
    def status(self):
        if self._status is None:
            res = self.gateway.list_statuswegsegmenten()
            for status in res:
                if int(status.id) == int(self.status_id):
                    self._status = status
        return self._status

    @property
    @check_lazy_load_wegsegment
    def methode(self):
        if self._methode is None:
            res = self.gateway.list_geometriemethodewegsegmenten()
            for methode in res:
                if int(methode.id) == int(self._methode_id):
                    self._methode = methode
        return self._methode

    @property
    @check_lazy_load_wegsegment
    def geometrie(self):
        return self._geometrie

    @property
    @check_lazy_load_wegsegment
    def metadata(self):
        return self._metadata

    def __unicode__(self):
        return "Wegsegment %s" % (self.id)

    def __repr__(self):
        return "Wegsegment(%s)" % (self.id)


def check_lazy_load_terreinobject(f):
    """
    Decorator function to lazy load a :class:`Terreinobject`.
    """

    def wrapper(*args):
        terreinobject = args[0]
        if (
            terreinobject._centroid is None
            or terreinobject._bounding_box is None
            or terreinobject._metadata is None
        ):
            log.debug("Lazy loading Terreinobject %s", terreinobject.id)
            terreinobject.check_gateway()
            t = terreinobject.gateway.get_terreinobject_by_id(terreinobject.id)
            terreinobject._centroid = t._centroid
            terreinobject._bounding_box = t._bounding_box
            terreinobject._metadata = t._metadata
        return f(*args)

    return wrapper


class Terreinobject(GatewayObject):
    """
    A cadastral parcel.

    A :class:`Terreinobject` is somewhat different from a :class:`Perceel`
    in the source of the data and the information provided. eg. A
    `terreinobject` has a `centroid` and a `bounding box`, while a `perceel`
    also has the centroid, but not the `bounding box`.
    """

    def __init__(
        self, id, aard, centroid=None, bounding_box=None, metadata=None, **kwargs
    ):
        self.id = id
        try:
            self.aard_id = aard.id
            self._aard = aard
        except AttributeError:
            self.aard_id = aard
            self._aard = None
        self._centroid = centroid
        self._metadata = metadata
        self._bounding_box = bounding_box
        super().__init__(**kwargs)

    @property
    def aard(self):
        if self._aard is None:
            res = self.gateway.list_aardterreinobjecten()
            for aard in res:
                if int(aard.id) == int(self.aard_id):
                    self._aard = aard
        return self._aard

    @property
    @check_lazy_load_terreinobject
    def centroid(self):
        return self._centroid

    @property
    @check_lazy_load_terreinobject
    def bounding_box(self):
        return self._bounding_box

    @property
    @check_lazy_load_terreinobject
    def metadata(self):
        return self._metadata

    def __unicode__(self):
        return "Terreinobject %s" % (self.id)

    def __repr__(self):
        return "Terreinobject(%s)" % (self.id)


def check_lazy_load_perceel(f):
    """
    Decorator function to lazy load a :class:`Perceel`.
    """

    def wrapper(*args):
        perceel = args[0]
        if perceel._centroid is None or perceel._metadata is None:
            log.debug("Lazy loading Perceel %s", perceel.id)
            perceel.check_gateway()
            p = perceel.gateway.get_perceel_by_id(perceel.id)
            perceel._centroid = p._centroid
            perceel._metadata = p._metadata
        return f(*args)

    return wrapper


class Perceel(GatewayObject):
    """
    A cadastral Parcel.

    A :class:`Terreinobject` is somewhat different from a :class:`Perceel`
    in the source of the data and the information provided. eg. A
    `terreinobject` has a `centroid` and a `bounding box`, while a `perceel`
    also has the centroid, but not the `bounding box`.
    """

    def __init__(self, id, centroid=None, metadata=None, **kwargs):
        self.id = id
        self._centroid = centroid
        self._metadata = metadata
        super().__init__(**kwargs)

    @property
    @check_lazy_load_perceel
    def centroid(self):
        return self._centroid

    @property
    @check_lazy_load_perceel
    def metadata(self):
        return self._metadata

    @property
    def huisnummers(self):
        """
        Returns the huisnummers on this Perceel.

        Some of the huisnummers might no longer be active.

        :rtype: list
        """
        self.check_gateway()
        return self.gateway.list_huisnummers_by_perceel(self.id)

    @property
    def postadressen(self):
        """
        Returns the postadressen for this Perceel.

        Will only take the huisnummers with status `inGebruik` into account.

        :rtype: list
        """
        return [h.postadres for h in self.huisnummers if h.status.id == "3"]

    def __unicode__(self):
        return "Perceel %s" % (self.id)

    def __repr__(self):
        return "Perceel(%s)" % (self.id)


def check_lazy_load_gebouw(f):
    """
    Decorator function to lazy load a :class:`Gebouw`.
    """

    def wrapper(*args):
        gebouw = args[0]
        if (
            gebouw._methode_id is None
            or gebouw._geometrie is None
            or gebouw._metadata is None
        ):
            log.debug("Lazy loading Gebouw %d", gebouw.id)
            gebouw.check_gateway()
            g = gebouw.gateway.get_gebouw_by_id(gebouw.id)
            gebouw._methode_id = g._methode_id
            gebouw._geometrie = g._geometrie
            gebouw._metadata = g._metadata
        return f(*args)

    return wrapper


class Gebouw(GatewayObject):
    """
    A building.
    """

    def __init__(
        self, id, aard, status, methode=None, geometrie=None, metadata=None, **kwargs
    ):
        self.id = int(id)
        try:
            self.aard_id = aard.id
            self._aard = aard
        except Exception:
            self.aard_id = aard
            self._aard = None
        try:
            self.status_id = status.id
            self._status = status
        except Exception:
            self.status_id = status
            self._status = None
        try:
            self._methode_id = methode.id
            self._methode = methode
        except Exception:
            self._methode_id = methode
            self._methode = None
        self._geometrie = geometrie
        self._metadata = metadata
        super().__init__(**kwargs)

    @property
    def aard(self):
        if self._aard is None:
            self.check_gateway()
            res = self.gateway.list_aardgebouwen()
            for aard in res:
                if int(aard.id) == int(self.aard_id):
                    self._aard = aard
        return self._aard

    @property
    def status(self):
        if self._status is None:
            self.check_gateway()
            res = self.gateway.list_statusgebouwen()
            for status in res:
                if int(status.id) == int(self.status_id):
                    self._status = status
        return self._status

    @property
    @check_lazy_load_gebouw
    def methode(self):
        if self._methode is None:
            res = self.gateway.list_geometriemethodegebouwen()
            for methode in res:
                if int(methode.id) == int(self._methode_id):
                    self._methode = methode
        return self._methode

    @property
    @check_lazy_load_gebouw
    def geometrie(self):
        return self._geometrie

    @property
    @check_lazy_load_gebouw
    def metadata(self):
        return self._metadata

    def __unicode__(self):
        return "Gebouw %s" % (self.id)

    def __repr__(self):
        return "Gebouw(%s)" % (self.id)


def check_lazy_load_subadres(f):
    """
    Decorator function to lazy load a :class:`Subadres`.
    """

    def wrapper(*args):
        subadres = args[0]
        if (
            subadres._metadata is None
            or subadres.aard_id is None
            or subadres.huisnummer_id is None
        ):
            log.debug("Lazy loading Subadres %d", subadres.id)
            subadres.check_gateway()
            s = subadres.gateway.get_subadres_by_id(subadres.id)
            subadres._metadata = s._metadata
            subadres.aard_id = s.aard_id
            subadres.huisnummer_id = s.huisnummer_id
        return f(*args)

    return wrapper


class Subadres(GatewayObject):
    """
    An address within a certain :class:`Huisnummer`.

    These can eg. be postboxes within an appartment complex.
    """

    def __init__(
        self, id, subadres, status, huisnummer_id=None, aard=None, metadata=None, **kwargs
    ):
        self.id = int(id)
        self.subadres = subadres
        try:
            self.status_id = status.id
            self._status = status
        except AttributeError:
            self.status_id = status
            self._status = None
        self.huisnummer_id = huisnummer_id
        try:
            self.aard_id = aard.id
            self._aard = aard
        except AttributeError:
            self.aard_id = aard
            self._aard = None
        self._metadata = metadata
        super().__init__(**kwargs)

    @property
    def huisnummer(self):
        self.check_gateway()
        return self.gateway.get_huisnummer_by_id(self.huisnummer_id)

    @property
    @check_lazy_load_subadres
    def metadata(self):
        return self._metadata

    @property
    def status(self):
        if self._status is None:
            res = self.gateway.list_statushuisnummers()
            for status in res:
                if int(status.id) == int(self.status_id):
                    self._status = status
        return self._status

    @property
    @check_lazy_load_subadres
    def aard(self):
        if self._aard is None:
            res = self.gateway.list_aardsubadressen()
            for aard in res:
                if int(aard.id) == int(self.aard_id):
                    self._aard = aard
        return self._aard

    @property
    def postadres(self):
        self.check_gateway()
        return self.gateway.get_postadres_by_subadres(self.id)

    @property
    def adresposities(self):
        self.check_gateway()
        return self.gateway.list_adresposities_by_subadres(self.id)

    def __unicode__(self):
        return f"{self.subadres} ({self.id})"

    def __repr__(self):
        return f"Subadres({self.id}, {self.status_id}, '{self.subadres}', {self.huisnummer_id})"


def check_lazy_load_adrespositie(f):
    """
    Decorator function to lazy load a :class:`Adrespositie`.
    """

    def wrapper(*args):
        adrespositie = args[0]
        if (
            adrespositie._geometrie is None
            or adrespositie._aard is None
            or adrespositie._metadata is None
        ):
            log.debug("Lazy loading Adrespositie %d", adrespositie.id)
            adrespositie.check_gateway()
            a = adrespositie.gateway.get_adrespositie_by_id(adrespositie.id)
            adrespositie._geometrie = a._geometrie
            adrespositie.aard_id = a.aard_id
            adrespositie._metadata = a._metadata
        return f(*args)

    return wrapper


class Adrespositie(GatewayObject):
    """
    The position of an `Adres`.

    This can be used for the position of both :class:`Huisnummer` and
    :class:`Subadres`.

    A `Huisnummer` or `Subadres`, can have more than one `Adrespositie`, each
    offering a different interpretation of the position of the `Adres`. See
    the `herkomst` and `aard` of each `Adrespositie` to know which one to pick.
    """

    def __init__(self, id, herkomst, geometrie=None, aard=None, metadata=None, **kwargs):
        self.id = id
        try:
            self.herkomst_id = herkomst.id
            self._herkomst = herkomst
        except AttributeError:
            self.herkomst_id = herkomst
            self._herkomst = None
        self._geometrie = geometrie
        try:
            self.aard_id = aard.id
            self._aard = aard
        except AttributeError:
            self.aard_id = aard
            self._aard = None
        self._metadata = metadata
        super().__init__(**kwargs)

    @property
    def herkomst(self):
        if self._herkomst is None:
            self.check_gateway()
            res = self.gateway.list_herkomstadresposities()
            for herkomst in res:
                if int(herkomst.id) == int(self.herkomst_id):
                    self._herkomst = herkomst
        return self._herkomst

    @property
    @check_lazy_load_adrespositie
    def metadata(self):
        return self._metadata

    @property
    @check_lazy_load_adrespositie
    def geometrie(self):
        return self._geometrie

    @property
    @check_lazy_load_adrespositie
    def aard(self):
        if self._aard is None:
            res = self.gateway.list_aardadressen()
            for aard in res:
                if int(aard.id) == int(self.aard_id):
                    self._aard = aard
        return self._aard

    def __unicode__(self):
        return "Adrespositie %s" % (self.id)

    def __repr__(self):
        return f"Adrespositie({self.id}, {self.herkomst_id})"


class Metadata(GatewayObject):
    """
    Metadata about a `straat`, `huisnummer`, ...

    Some of the metadata available is the datum the object was created, the
    organisation that created it and the type of creation.
    """

    def __init__(
        self, begin_datum, begin_tijd, begin_bewerking, begin_organisatie, **kwargs
    ):
        self.begin_datum = str(begin_datum)
        self.begin_tijd = str(begin_tijd)
        try:
            self._begin_bewerking_id = begin_bewerking.id
            self._begin_bewerking = begin_bewerking
        except AttributeError:
            self._begin_bewerking_id = begin_bewerking
            self._begin_bewerking = None
        try:
            self._begin_organisatie_id = begin_organisatie.id
            self._begin_organisatie = begin_organisatie
        except AttributeError:
            self._begin_organisatie_id = begin_organisatie
            self._begin_organisatie = None
        super().__init__(**kwargs)

    @property
    def begin_bewerking(self):
        if self._begin_bewerking is None:
            self.check_gateway()
            bewerkingen = self.gateway.list_bewerkingen()
            for bewerking in bewerkingen:
                if int(bewerking.id) == int(self._begin_bewerking_id):
                    self._begin_bewerking = bewerking
        return self._begin_bewerking

    @property
    def begin_organisatie(self):
        if self._begin_organisatie is None:
            self.check_gateway()
            organisaties = self.gateway.list_organisaties()
            for organisatie in organisaties:
                if int(organisatie.id) == int(self._begin_organisatie_id):
                    self._begin_organisatie = organisatie
        return self._begin_organisatie

    def __unicode__(self):
        return "Begin datum: %s" % (self.begin_datum)
