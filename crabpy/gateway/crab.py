# -*- coding: utf-8 -*-
'''
This module contains an opionated gateway for the crab webservice.

.. versionadded:: 0.3.0
'''

from __future__ import unicode_literals

from crabpy.client import crab_request

from suds import WebFault

from crabpy.gateway.exception import (
    GatewayRuntimeException
)

from dogpile.cache import make_region


def crab_gateway_request(client, method, *args):
    '''
    Utility function that helps making requests to the CRAB service.

    This is a specialised version of :func:`crabpy.client.crab_request` that
    allows adding extra functionality for the calls made by the gateway.

    :param client: A :class:`suds.client.Client` for the CRAB service.
    :param string action: Which method to call, eg. `ListGewesten`
    :returns: Result of the SOAP call.
    '''
    try:
        return crab_request(client, method, *args)
    except WebFault as wf:
        err = GatewayRuntimeException(
            'Could not execute request. Message from server:\n%s' % wf.fault['faultstring'],
            wf
        )
        raise err


class CrabGateway(object):
    '''
    A gateway to the CRAB webservice.
    '''
    caches = {}

    def __init__(self, client, **kwargs):
        self.client = client
        cache_regions = ['permanent', 'long', 'short']
        for cr in cache_regions:
            self.caches[cr] = make_region(key_mangler=str)
        if 'cache_config' in kwargs:
            for cr in cache_regions:
                if ('%s.backend' % cr) in kwargs['cache_config']:
                    self.caches[cr].configure_from_config(
                        kwargs['cache_config'],
                        '%s.' % cr
                    )

    def list_gewesten(self, sort=1):
        '''
        List all `gewesten` in Belgium.

        :param integer sort: What field to sort on.
        :rtype: A :class`list` of class: `Gewest`.
        '''
        def creator():
            res = crab_gateway_request(self.client, 'ListGewesten', sort)
            return[
                Gewest(
                    r.GewestId,
                    r.GewestNaam
                )for r in res.GewestItem
            ]
        if self.caches['permanent'].is_configured:
            key = 'ListGewesten#%s' % sort
            gewesten = self.caches['permanent'].get_or_create(key, creator)
        else:
            gewesten = creator()
        for g in gewesten:
            g.set_gateway(self)
        return gewesten

    def list_gemeenten(self, gewest=2, sort=1):
        '''
        List all `gemeenten` in a `gewest`.

        :param gewest: The :class:`Gewest` for which the \
            `gemeenten` are wanted.
        :param integer sort: What field to sort on.
        :rtype: A :class:`list` of :class:`Gemeente`.
        '''
        try:
            id = gewest.id
        except AttributeError:
            id = gewest

        def creator():
            res = crab_gateway_request(
                self.client, 'ListGemeentenByGewestId', id, sort
            )
            return[
                Gemeente(
                    r.GemeenteId,
                    r.GemeenteNaam,
                    r.NISGemeenteCode,
                    Gewest(id)
                )for r in res.GemeenteItem
            ]
        if self.caches['long'].is_configured:
            key = 'ListGemeentenByGewestId#%s%s' % (id, sort)
            gemeenten = self.caches['long'].get_or_create(key, creator)
        else:
            gemeenten = creator()
        for g in gemeenten:
            g.set_gateway(self)
            g.gewest.set_gateway(self)
        return gemeenten

    def get_gemeente_by_id(self, id):
        '''
        Retrieve a `gemeente` by the crab id.

        :param integer id: The CRAB id of the gemeente.
        :rtype: :class:`Gemeente`
        '''
        def creator():
            res = crab_gateway_request(
                self.client, 'GetGemeenteByGemeenteId', id
            )
            return Gemeente(
                res.GemeenteId,
                res.GemeenteNaam,
                res.NisGemeenteCode,
                res.GewestId,
                res.TaalCode,
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY),
                res.BeginDatum,
                res.BeginTijd,
                res.BeginBewerking,
                res.BeginOrganisatie
            )
        if self.caches['long'].is_configured:
            key = 'GetGemeenteByGemeenteId#%s' % id
            gemeente = self.caches['long'].get_or_create(key, creator)
        else:
            gemeente = creator()
        gemeente.set_gateway(self)
        return gemeente

    def get_gemeente_by_niscode(self, niscode):
        '''
        Retrieve a `gemeente` by the NIScode.

        :param integer niscode: The NIScode of the gemeente.
        :rtype: :class:`Gemeente`
        '''

        def creator():
            res = crab_gateway_request(
                self.client, 'GetGemeenteByNISGemeenteCode', niscode
            )
            return Gemeente(
                res.GemeenteId,
                res.GemeenteNaam,
                res.NisGemeenteCode,
                res.GewestId,
                res.TaalCode,
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY),
                res.BeginDatum,
                res.BeginTijd,
                res.BeginBewerking,
                res.BeginOrganisatie
            )
        if self.caches['long'].is_configured:
            key = 'GetGemeenteByNISGemeenteCode#%s' % niscode
            gemeente = self.caches['long'].get_or_create(key, creator)
        else:
            gemeente = creator()
        gemeente.set_gateway(self)
        return gemeente

    def _list_codeobject(self, function, sort, returnclass):
        def creator():
            res = crab_gateway_request(self.client, function, sort)
            return[
                globals()[returnclass](
                    r.Code,
                    r.Naam,
                    r.Definitie
                )for r in res.CodeItem
            ]
        if self.caches['permanent'].is_configured:
            key = function+'#%s' % (sort)
            return self.caches['permanent'].get_or_create(key, creator)
        else:
            return creator()

    def list_talen(self, sort=1):
        '''
        List all `talen`.

        :rtype: A :class:`list` of :class:`Taal`
        '''
        return self._list_codeobject('ListTalen', sort, 'Taal')

    def list_bewerkingen(self, sort=1):
        '''
        List all `bewerkingen`.

        :rtype: A :class:`list` of :class:`Bewerking`
        '''
        return self._list_codeobject(
            'ListBewerkingen', sort, 'Bewerking'
        )

    def list_organisaties(self, sort=1):
        '''
        List all `organisaties`.

        :rtype: A :class:`list` of :class:`Organisatie`
        '''
        return self._list_codeobject(
            'ListOrganisaties', sort, 'Organisatie'
        )

    def list_aardsubadressen(self, sort=1):
        '''
        List all `aardsubadressen`.

        :rtype: A :class:`list` of :class:`Aardsubadres`
        '''
        return self._list_codeobject(
            'ListOrganisaties', sort, 'Aardsubadres'
        )

    def list_aardadressen(self, sort=1):
        '''
        List all `aardadressen`.

        :rtype: A :class:`list` of :class:`Aardadres`
        '''
        return self._list_codeobject(
            'ListAardAdressen', sort, 'Aardadres'
        )

    def list_aardgebouwen(self, sort=1):
        '''
        List all `aardgebouwen`.

        :rtype: A :class:`list` of :class:`Aardgebouw`
        '''
        return self._list_codeobject(
            'ListAardGebouwen', sort, 'Aardgebouw'
        )

    def list_aardwegobjecten(self, sort=1):
        '''
        List all `aardwegobjecten`.

        :rtype: A :class:`list` of :class:`Aardwegobject`
        '''
        return self._list_codeobject(
            'ListAardWegobjecten', sort, 'Aardwegobject'
        )

    def list_aardterreinobjecten(self, sort=1):
        '''
        List all `aardterreinobjecten`.

        :rtype: A :class:`list` of :class:`Aardterreinobject`
        '''
        return self._list_codeobject(
            'ListAardTerreinobjecten', sort, 'Aardterreinobject'
        )

    def list_statushuisnummers(self, sort=1):
        '''
        List all `statushuisnummers`.

        :rtype: A :class:`list` of :class:`Statushuisnummer`
        '''
        return self._list_codeobject(
            'ListStatusHuisnummers', sort, 'Statushuisnummer'
        )

    def list_statussubadressen(self, sort=1):
        '''
        List all `statussubadressen`.

        :rtype: A :class:`list` of :class:`Statussubadres`
        '''
        return self._list_codeobject(
            'ListStatusSubadressen', sort, 'Statussubadres'
        )

    def list_statusstraatnamen(self, sort=1):
        '''
        List all `statusstraatnamen`.

        :rtype: A :class:`list` of :class:`Statusstraatnaam`
        '''
        return self._list_codeobject(
            'ListStatusStraatnamen', sort, 'Statusstraatnaam'
        )

    def list_statuswegsegmenten(self, sort=1):
        '''
        List all `statuswegsegmenten`.

        :rtype: A :class:`list` of :class:`Statuswegsegment`
        '''
        return self._list_codeobject(
            'ListStatusWegsegmenten', sort, 'Statuswegsegment'
        )

    def list_geometriemethodewegsegmenten(self, sort=1):
        '''
        List all `geometriemethodewegsegmenten`.

        :rtype: A :class:`list` of :class:`Geometriemethodewegsegment`
        '''
        return self._list_codeobject(
            'ListGeometriemethodeWegsegmenten', sort,
            'Geometriemethodewegsegment'
        )

    def list_statusgebouwen(self, sort=1):
        '''
        List all `statusgebouwen`.

        :rtype: A :class:`list` of :class:`Statusgebouwen`
        '''
        return self._list_codeobject(
            'ListStatusGebouwen', sort, 'Statusgebouw'
        )

    def list_geometriemethodegebouwen(self, sort=1):
        '''
        List all `geometriegebouwen`.

        :rtype: A :class:`list` of :class:`Geometriegebouw`
        '''
        return self._list_codeobject(
            'ListGeometriemethodeGebouwen', sort, 'Geometriemethodegebouw'
        )

    def list_herkomstadresposities(self, sort=1):
        '''
        List all `herkomstadresposities`.

        :rtype: A :class:`list` of :class:`Herkomstadrespositie`
        '''
        return self._list_codeobject(
            'ListHerkomstAdresposities', sort, 'Herkomstadrespositie'
        )

    def list_straten(self, gemeente, sort=1):
        '''
        List all `straten` in a `Gemeente`.

        :param gemeente: The :class:`Gemeente` for which the \
            `straten` are wanted.
        :rtype: A :class:`list` of :class:`Straat`
        '''
        try:
            id = gemeente.id
        except AttributeError:
            id = gemeente

        def creator():
            res = crab_gateway_request(
                self.client, 'ListStraatnamenWithStatusByGemeenteId',
                id, sort
            )
            return[
                Straat(
                    r.StraatnaamId,
                    r.StraatnaamLabel,
                    r.StatusStraatnaam
                )for r in res.StraatnaamWithStatusItem
            ]
        if self.caches['long'].is_configured:
            key = 'ListStraatnamenWithStatusByGemeenteId#%s%s' % (id, sort)
            straten = self.caches['long'].get_or_create(key, creator)
        else:
            straten = creator()
        for s in straten:
            s.set_gateway(self)
        return straten

    def get_straat_by_id(self, id):
        '''
        Retrieve a `straat` by the Id.

        :param integer id: The id of the `straat`.
        :rtype: :class:`Straat`
        '''
        def creator():
            res = crab_gateway_request(
                self.client, 'GetStraatnaamWithStatusByStraatnaamId', id
            )
            return Straat(
                res.StraatnaamId,
                res.StraatnaamLabel,
                res.StatusStraatnaam,
                res.Straatnaam,
                res.TaalCode,
                res.StraatnaamTweedeTaal,
                res.TaalCodeTweedeTaal,
                res.GemeenteId,
                res.BeginDatum,
                res.BeginTijd,
                res.BeginBewerking,
                res.BeginOrganisatie
            )

        if self.caches['long'].is_configured:
            key = 'GetStraatnaamWithStatusByStraatnaamId#%s' % (id)
            straat = self.caches['long'].get_or_create(key, creator)
        else:
            straat = creator()
        straat.set_gateway(self)
        return straat

    def list_huisnummers_by_straat(self, straat, sort=1):
        '''
        List all `huisnummers` in a `Straat`.

        :param straat: The :class:`Straat` for which the \
            `huisnummers` are wanted.
        :rtype: A :class: `list` of :class:`Huisnummer`
        '''
        try:
            id = straat.id
        except AttributeError:
            id = straat

        def creator():
            res = crab_gateway_request(
                self.client, 'ListHuisnummersWithStatusByStraatnaamId',
                id, sort
            )
            return[
                Huisnummer(
                    r.HuisnummerId,
                    r.StatusHuisnummer,
                    r.Huisnummer
                ) for r in res.HuisnummerWithStatusItem
            ]
        if self.caches['long'].is_configured:
            key = 'ListHuisnummersWithStatusByStraatnaamId#%s%s' % (id, sort)
            huisnummers = self.caches['long'].get_or_create(key, creator)
        else:
            huisnummers = creator()
        for h in huisnummers:
            h.set_gateway(self)
        return huisnummers

    def get_huisnummer_by_id(self, id):
        '''
        Retrieve a `huisnummer` by the Id.

        :param integer id: the Id of the `huisnummer`
        :rtype: :class:`Huisnummer`
        '''
        def creator():
            res = crab_gateway_request(
                self.client, 'GetHuisnummerWithStatusByHuisnummerId', id
            )
            return Huisnummer(
                res.HuisnummerId,
                res.StatusHuisnummer,
                res.Huisnummer,
                res.StraatnaamId,
                res.BeginDatum,
                res.BeginTijd,
                res.BeginBewerking,
                res.BeginOrganisatie
            )
        if self.caches['long'].is_configured:
            key = 'GetHuisnummerWithStatusByHuisnummerId#%s' % (id)
            huisnummer = self.caches['long'].get_or_create(key, creator)
        else:
            huisnummer = creator()
        huisnummer.set_gateway(self)
        return huisnummer

    def get_huisnummer_by_nummer_and_straat(self, nummer, straat):
        '''
        Retrieve a `huisnummer` by the `nummer` and `straat`

        :param integer nummer: The huisnummer of the 'huisnummer`
        :param straat: The :class:`Straat` in which the `huisnummer` \
            is situated.
        :rtype: A :class:`Huisnummer`
        '''
        try:
            straat_id = straat.id
        except AttributeError:
            straat_id = straat

        def creator():
            res = crab_gateway_request(
                self.client, 'GetHuisnummerWithStatusByHuisnummer',
                nummer, straat_id
            )
            return Huisnummer(
                res.HuisnummerId,
                res.StatusHuisnummer,
                res.Huisnummer,
                res.StraatnaamId
            )
        if self.caches['long'].is_configured:
            key = 'GetHuisnummerWithStatusByHuisnummer#%s%s' % (nummer, straat_id)
            huisnummer = self.caches['long'].get_or_create(key, creator)
        else:
            huisnummer = creator()
        huisnummer.set_gateway(self)
        return huisnummer

    def list_postkantons_by_gemeente(self, gemeente):
        '''
        List all `postkantons` in a :class:`Gemeente`

        :param gemeente: The :class:`Gemeente` for which the \
            `potkantons` are wanted.
        :rtype: A :class:`list` of :class:`Postkanton`
        '''
        try:
            id = gemeente.id
        except AttributeError:
            id = gemeente

        def creator():
            res = crab_gateway_request(
                self.client, 'ListPostkantonsByGemeenteId', id
            )
            return[
                Postkanton(
                    r.PostkantonCode,
                    id
                )for r in res.PostkantonItem
            ]
        if self.caches['long'].is_configured:
            key = 'ListPostkantonsByGemeenteId#%s' % (id)
            postkantons = self.caches['long'].get_or_create(key, creator)
        else:
            postkantons = creator()
        for r in postkantons:
            r.set_gateway(self)
        return postkantons

    def get_postkanton_by_huisnummer(self, huisnummer):
        '''
        Retrieve a `postkanton` by the Huisnummer.

        :param huisnummer: The :class:`Huisnummer` for which the `postkanton` \
                is wanted.
        :rtype: :class:`Postkanton`
        '''
        try:
            id = huisnummer.id
        except AttributeError:
            id = huisnummer

        def creator():
            huisnummer = Huisnummer(id)
            huisnummer.set_gateway(self)
            gemeente_id = huisnummer.straat.gemeente.id
            res = crab_gateway_request(
                self.client, 'GetPostkantonByHuisnummerId', id
            )
            return Postkanton(
                res.PostkantonCode,
                gemeente_id,
                res.BeginDatum,
                res.BeginTijd,
                res.BeginBewerking,
                res.BeginOrganisatie
            )
        if self.caches['long'].is_configured:
            key = 'GetPostkantonByHuisnummerId#%s' % (id)
            postkanton = self.caches['long'].get_or_create(key, creator)
        else:
            postkanton = creator()
        postkanton.set_gateway(self)
        return postkanton

    def get_wegobject_by_id(self, id):
        '''
        Retrieve a `Wegobject` by the Id.

        :param integer id: the Id of the `Wegobject`
        :rtype: :class:`Wegobject`
        '''
        def creator():
            res = crab_gateway_request(
                self.client, 'GetWegobjectByIdentificatorWegobject', id
            )
            return Wegobject(
                res.IdentificatorWegobject,
                res.AardWegobject,
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY),
                res.BeginDatum,
                res.BeginTijd,
                res.BeginBewerking,
                res.BeginOrganisatie
            )
        if self.caches['long'].is_configured:
            key = 'GetWegobjectByIdentificatorWegobject#%s' % (id)
            wegobject = self.caches['long'].get_or_create(key, creator)
        else:
            wegobject = creator()
        wegobject.set_gateway(self)
        return wegobject

    def list_wegobjecten_by_straat(self, straat):
        '''
        List all `wegobjecten` in a :class:`Straat`
 
        :param straat: The :class:`Straat` for which the `wegobjecten` \
                are wanted.
        :rtype: A :class:`list` of :class:`Wegobject`
        '''
        try:
            id = straat.id
        except AttributeError:
            id = straat

        def creator():
            res = crab_gateway_request(
                self.client, 'ListWegobjectenByStraatnaamId', id
            )
            return [
                Wegobject(
                    r.IdentificatorWegobject,
                    r.AardWegobject
                )for r in res.WegobjectItem
            ]
        if self.caches['long'].is_configured:
            key = 'ListWegobjectenByStraatnaamId#%s' % (id)
            wegobjecten = self.caches['long'].get_or_create(key, creator)
        else:
            wegobjecten = creator()
        for r in wegobjecten:
            r.set_gateway(self)
        return wegobjecten

    def get_wegsegment_by_id(self, id):
        '''
        Retrieve a `wegsegment` by the Id.

        :param integer id: the Id of the `wegsegment`
        :rtype: :class:`Wegsegment`
        '''
        def creator():
            res = crab_gateway_request(
                self.client,
                'GetWegsegmentByIdentificatorWegsegment', id
            )
            return Wegsegment(
                res.IdentificatorWegsegment,
                res.StatusWegsegment,
                res.GeometriemethodeWegsegment,
                res.Geometrie,
                res.BeginDatum,
                res.BeginTijd,
                res.BeginBewerking,
                res.BeginOrganisatie
            )
        if self.caches['long'].is_configured:
            key = 'GetWegsegmentByIdentificatorWegsegment#%s' % (id)
            wegsegment = self.caches['long'].get_or_create(key, creator)
        else:
            wegsegment = creator()
        wegsegment.set_gateway(self)
        return wegsegment

    def list_wegsegmenten_by_straat(self, straat):
        '''
        List all `wegsegmenten` in a :class:`Straat`

        :param straat: The :class:`Straat` for which the `wegsegmenten` \
                are wanted.
        :rtype: A :class:`list` of :class:`Wegsegment`
        '''
        try:
            id = straat.id
        except AttributeError:
            id = straat

        def creator():
            res = crab_gateway_request(
                self.client, 'ListWegsegmentenByStraatnaamId', id
            )
            return[
                Wegsegment(
                    r.IdentificatorWegsegment,
                    r.StatusWegsegment
                )for r in res.WegsegmentItem
            ]
        if self.caches['long'].is_configured:
            key = 'ListWegsegmentenByStraatnaamId#%s' % (id)
            wegsegmenten = self.caches['long'].get_or_create(key, creator)
        else:
            wegsegmenten = creator()
        for r in wegsegmenten:
            r.set_gateway(self)
        return wegsegmenten

    def list_terreinobjecten_by_huisnummer(self, huisnummer):
        '''
        List all `terreinobjecten` for a :class:`Huisnummer`

        :param huisnummer: The :class:`Huisnummer` for which the \
            `terreinobjecten` are wanted.
        :rtype: A :class:`list` of :class:`Terreinobject`
        '''
        try:
            id = huisnummer.id
        except AttributeError:
            id = huisnummer

        def creator():
            res = crab_gateway_request(
                self.client, 'ListTerreinobjectenByHuisnummerId', id
            )
            return[
                Terreinobject(
                    r.IdentificatorTerreinobject,
                    r.AardTerreinobject
                )for r in res.TerreinobjectItem
            ]
        if self.caches['long'].is_configured:
            key = 'ListTerreinobjectenByHuisnummerId#%s' % (id)
            terreinobjecten = self.caches['long'].get_or_create(key, creator)
        else:
            terreinobjecten = creator()
        for r in terreinobjecten:
            r.set_gateway(self)
        return terreinobjecten

    def get_terreinobject_by_id(self, id):
        '''
        Retrieve a `Terreinobject` by the Id.

        :param integer id: the Id of the `Terreinobject`
        :rtype: :class:`Terreinobject`
        '''
        def creator():
            res = crab_gateway_request(
                self.client,
                'GetTerreinobjectByIdentificatorTerreinobject', id
            )
            return Terreinobject(
                res.IdentificatorTerreinobject,
                res.AardTerreinobject,
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY),
                res.BeginDatum,
                res.BeginTijd,
                res.BeginBewerking,
                res.BeginOrganisatie
            )
        if self.caches['long'].is_configured:
            key = 'GetTerreinobjectByIdentificatorTerreinobject#%s' % (id)
            terreinobject = self.caches['long'].get_or_create(key, creator)
        else:
            terreinobject = creator()
        terreinobject.set_gateway(self)
        return terreinobject

    def list_percelen_by_huisnummer(self, huisnummer):
        '''
        List all `percelen` for a :class:`Huisnummer`

        :param huisnummer: The :class:`Huisnummer` for which the \
            `percelen` are wanted.
        :rtype: A :class:`list` of :class:`Perceel`
        '''
        try:
            id = huisnummer.id
        except AttributeError:
            id = huisnummer

        def creator():
            res = crab_gateway_request(
                self.client, 'ListPercelenByHuisnummerId', id
            )
            return [
                Perceel(
                    r.IdentificatorPerceel
                )for r in res.PerceelItem
            ]
        if self.caches['long'].is_configured:
            key = 'ListPercelenByHuisnummerId#%s' % (id)
            percelen = self.caches['long'].get_or_create(key, creator)
        else:
            percelen = creator()
        for r in percelen:
            r.set_gateway(self)
        return percelen

    def get_perceel_by_id(self, id):
        '''
        Retrieve a `Perceel` by the Id.

        :param string id: the Id of the `Perceel`
        :rtype: :class:`Perceel`
        '''
        def creator():
            res = crab_gateway_request(
                self.client, 'GetPerceelByIdentificatorPerceel', id
            )
            return Perceel(
                res.IdentificatorPerceel,
                (res.CenterX, res.CenterY),
                res.BeginDatum,
                res.BeginTijd,
                res.BeginBewerking,
                res.BeginOrganisatie
            )
        if self.caches['long'].is_configured:
            key = 'GetPerceelByIdentificatorPerceel#%s' % (id)
            perceel = self.caches['long'].get_or_create(key, creator)
        else:
            perceel = creator()
        perceel.set_gateway(self)
        return perceel

    def list_gebouwen_by_huisnummer(self, huisnummer):
        '''
        List all `gebouwen` for a :class:`Huisnummer`.

        :param huisnummer: The :class:`Huisnummer` for which the \
            `gebouwen` are wanted.
        :rtype: A :class:`list` of :class:`Gebouw`
        '''
        try:
            id = huisnummer.id
        except AttributeError:
            id = huisnummer

        def creator():
            res = crab_gateway_request(
                self.client, 'ListGebouwenByHuisnummerId', id
            )
            return [
                Gebouw(
                    r.IdentificatorGebouw,
                    r.AardGebouw,
                    r.StatusGebouw
                )for r in res.GebouwItem
            ]
        if self.caches['long'].is_configured:
            key = 'ListGebouwenByHuisnummerId#%s' % (id)
            gebouwen = self.caches['long'].get_or_create(key, creator)
        else:
            gebouwen = creator()
        for r in gebouwen:
            r.set_gateway(self)
        return gebouwen

    def get_gebouw_by_id(self, id):
        '''
        Retrieve a `Gebouw` by the Id.

        :param integer id: the Id of the `Gebouw`
        :rtype: :class:`Gebouw`
        '''
        def creator():
            res = crab_gateway_request(
                self.client, 'GetGebouwByIdentificatorGebouw', id
            )
            return Gebouw(
                res.IdentificatorGebouw,
                res.AardGebouw,
                res.StatusGebouw,
                res.GeometriemethodeGebouw,
                res.Geometrie,
                res.BeginDatum,
                res.BeginTijd,
                res.BeginBewerking,
                res.BeginOrganisatie
            )
        if self.caches['long'].is_configured:
            key = 'GetGebouwByIdentificatorGebouw#%s' % (id)
            gebouw = self.caches['long'].get_or_create(key, creator)
        else:
            gebouw = creator()
        return gebouw


class GatewayObject(object):
    '''
    Abstract class for objects that are able to use a 
    :class:`crabpy.Gateway.CrabGateway` to find further information.
    '''

    gateway = None

    def __init__(self, **kwargs):
        if 'gateway' in kwargs:
            self.set_gateway(kwargs['gateway'])

    def set_gateway(self, gateway):
        self.gateway = gateway

    def check_gateway(self):
        if not self.gateway:
            raise RuntimeError("There's no Gateway I can use")


class Gewest(GatewayObject):
    '''
    A large administrative unit in Belgium.

    Belgium consists of 3 `gewesten`. Together they form the entire territory
    of the country.
    '''
    def __init__(
        self, id, naam=None,
        **kwargs
    ):
        self.id = int(id)
        self._naam = naam
        super(Gewest, self).__init__(**kwargs)

    @property
    def naam(self):
        return self._naam

    @property
    def gemeenten(self):
        return self.gateway.list_gemeenten(self.id)

    def __str__(self):
        if self.naam is not None:
            return "%s (%s)" % (self._naam, self.id)
        else:
            return "Gewest %s" % (self.id)

    def __repr__(self):
        if self.naam is not None:
            return"Gewest(%s, '%s')" % (self.id, self._naam)
        else:
            return "Gewest(%s)" % (self.id)


def check_lazy_load_gemeente(f):
    '''
    Decorator function to lazy load a :class:`Gemeente`.
    '''
    def wrapper(*args):
        gemeente = args[0]
        if (
            gemeente._naam is None or gemeente._centroid is None or
            gemeente._bounding_box is None or gemeente._niscode is None or
            gemeente._gewest_id is None or gemeente._taal_id is None or
            gemeente._metadata is None
        ):
            gemeente.check_gateway()
            g = gemeente.gateway.get_gemeente_by_id(gemeente.id)
            gemeente._naam = g._naam
            gemeente._niscode = g._niscode
            gemeente._gewest_id = g._gewest_id
            gemeente._taal_id = g._taal_id
            gemeente._centroid = g._centroid
            gemeente._bounding_box = g._bounding_box
            gemeente._metadata = g._metadata
        return f(*args)
    return wrapper


class Gemeente(GatewayObject):
    '''
    The smallest administrative unit in Belgium.
    '''
    def __init__(
            self, id, naam=None, niscode=None,
            gewest_id=None, taal_id=None, centroid=None,
            bounding_box=None, datum=None, tijd=None,
            bewerking_id=None, organisatie_id=None, **kwargs
    ):
        self.id = int(id)
        self._naam = naam
        self._niscode = niscode
        self._gewest_id = gewest_id
        self._taal_id = taal_id
        self._centroid = centroid
        self._bounding_box = bounding_box
        if (
            datum is not None and tijd is not None and
            bewerking_id is not None and organisatie_id is not None
        ):
            self._metadata = Metadata(
                datum, tijd, bewerking_id, organisatie_id
            )
        else:
            self._metadata = None
        super(Gemeente, self).__init__(**kwargs)

    @property
    @check_lazy_load_gemeente
    def naam(self):
        return self._naam

    @property
    @check_lazy_load_gemeente
    def niscode(self):
        return self._niscode

    @property
    @check_lazy_load_gemeente
    def gewest(self):
        res = self.gateway.list_gewesten()
        for r in res:
            if int(r.id) == int(self._gewest_id):
                return r

    @property
    @check_lazy_load_gemeente
    def taal(self):
        res = self.gateway.list_talen()
        for r in res:
            if r.id == self._taal_id:
                return r

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

    def __str__(self):
        if self._naam is not None:
            return "%s (%s)" % (self._naam, self.id)
        else:
            return "Gemeente %s" % (self.id)

    def __repr__(self):
        if self._naam is not None:
            return "Gemeente(%s, '%s')" % (self.id, self._naam)
        else:
            return "Gemeente(%s)" % (self.id)


class Codelijst(GatewayObject):
    def __init__(
            self, id, naam, definitie, **kwargs
    ):
        self.id = id
        self.naam = naam
        self.definitie = definitie
        super(Codelijst, self).__init__(**kwargs)

    def __str__(self):
        return self.naam


class Taal(Codelijst):
    '''
    A language.
    '''
    def __repr__(self):
        return "Taal(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


class Bewerking(Codelijst):
    '''
    An edit.
    '''
    def __repr__(self):
        return "Bewerking(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


class Organisatie(Codelijst):
    '''
    An organisation that played a role in the genessis of an object.
    '''
    def __repr__(self):
        return "Organisatie(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


class Aardsubadres(Codelijst):
    '''
    The nature of a subaddress.
    '''
    def __repr__(self):
        return "Aardsubadres(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


class Aardadres(Codelijst):
    '''
    The nature of an address.
    '''
    def __repr__(self):
        return "Aardadres(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


class Aardgebouw(Codelijst):
    '''
    The nature of a building.
    '''
    def __repr__(self):
        return "Aardgebouw(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


class Aardwegobject(Codelijst):
    '''
    The nature of a `wegobject`.
    '''
    def __repr__(self):
        return "Aardwegobject(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


class Aardterreinobject(Codelijst):
    '''
    The nature of a `terreinobject`.
    '''
    def __repr__(self):
        return "Aardterreinobject(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


class Statushuisnummer(Codelijst):
    '''
    The current state of a `huisnummer`.
    '''
    def __repr__(self):
        return "Statushuisnummer(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


class Statussubadres(Codelijst):
    '''
    The current state of a `subadres`.
    '''
    def __repr__(self):
        return "Statussubadres(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


class Statusstraatnaam(Codelijst):
    '''
    The current state of a `straatnaam`.
    '''
    def __repr__(self):
        return "Statusstraatnaam(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


class Statuswegsegment(Codelijst):
    '''
    The current state of a `wegsegment`.
    '''
    def __repr__(self):
        return "Statuswegsegment(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


class Geometriemethodewegsegment(Codelijst):
    '''
    The geometry method of a :class:`Wegsegment`.
    '''
    def __repr__(self):
        return "Geometriemethodewegsegment(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


class Statusgebouw(Codelijst):
    '''
    The current state of a :class:`Gebouw`.
    '''
    def __repr__(self):
        return "Statusgebouw(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


class Geometriemethodegebouw(Codelijst):
    '''
    The geometry method of a :class:`Gebouw`.
    '''
    def __repr__(self):
        return "Geometriemethodegebouw(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


class Herkomstadrespositie(Codelijst):
    '''
    The origin of an Adressposition.
    '''
    def __repr__(self):
        return "Herkomstadrespositie(%s, '%s', '%s')" % (self.id, self.naam, self.definitie)


def check_lazy_load_straat(f):
    '''
    Decorator function to lazy load a :class:`Straat`.
    '''
    def wrapper(*args):
        straat = args[0]
        if (
            straat._label is None or straat._namen is None or
            straat._status_id is None or straat._gemeente_id is None or
            straat._metadata is None
        ):
            straat.check_gateway()
            s = straat.gateway.get_straat_by_id(straat.id)
            straat._label = s._label
            straat._gemeente_id = s._gemeente_id
            straat._namen = s._namen
            straat._status_id = s._status_id
            straat._metadata = s._metadata
        return f(*args)
    return wrapper


class Straat(GatewayObject):
    '''
    A street.

    A street object is always located in one and exactly one :class:`Straat`.
    '''
    def __init__(
            self, id, label=None, status_id=None, straatnaam=None,
            taalcode=None, straatnaam2=None, taalcode2=None,
            gemeente_id=None, begin_datum=None, begin_tijd=None,
            begin_bewerking_id=None, begin_organisatie_id=None, **kwargs
    ):
        self.id = id
        self._label = label
        self._status_id = status_id
        self._namen = ((straatnaam, taalcode), (straatnaam2, taalcode2))
        self._gemeente_id = gemeente_id
        if (
            begin_datum is not None and begin_tijd is not None and
            begin_bewerking_id is not None and
            begin_organisatie_id is not None
        ):
            self._metadata = Metadata(
                begin_datum, begin_tijd, begin_bewerking_id,
                begin_organisatie_id
            )
        else:
            self._metadata = None
        super(Straat, self).__init__(**kwargs)

    @property
    @check_lazy_load_straat
    def label(self):
        return self._label

    @property
    @check_lazy_load_straat
    def namen(self):
        return self._namen

    @property
    @check_lazy_load_straat
    def gemeente(self):
        return self.gateway.get_gemeente_by_id(self._gemeente_id)

    @property
    @check_lazy_load_straat
    def status(self):
        res = self.gateway.list_statusstraatnamen()
        for r in res:
            if int(r.id) == int(self._status_id):
                return r

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

    def __str__(self):
        if self._label is not None:
            return "%s (%s)" % (self._label, self.id)
        else:
            return "Straat %s" % (self.id)

    def __repr__(self):
        if self._label is not None:
            return "Straat(%s, '%s')" % (self.id, self._label)
        else:
            return "Straat(%s)" % (self.id)


def check_lazy_load_huisnummer(f):
    '''
    Decorator function to lazy load a :class:`Huisnummer`.
    '''
    def wrapper(*args):
        huisnummer = args[0]
        if (
            huisnummer._straat_id is None or huisnummer._huisnummer
            is None or huisnummer._status_id is None or
            huisnummer._metadata is None
        ):
            huisnummer.check_gateway()
            h = huisnummer.gateway.get_huisnummer_by_id(huisnummer.id)
            huisnummer._straat_id = h._straat_id
            huisnummer._huisnummer = h._huisnummer
            huisnummer._status_id = h._status_id
            huisnummer._metadata = h._metadata
        return f(*args)
    return wrapper


class Huisnummer(GatewayObject):
    '''
    A house number.

    This is mainly a combination of a street and a house number.
    '''
    def __init__(
            self, id, status_id=None, huisnummer=None,
            straat_id=None, datum=None, tijd=None,
            bewerking_id=None, organisatie_id=None, **kwargs
    ):
        self.id = int(id)
        self._status_id = status_id
        self._huisnummer = huisnummer
        self._straat_id = straat_id
        if (
            datum is not None and tijd is not None and
            bewerking_id is not None and organisatie_id is not None
        ):
            self._metadata = Metadata(
                datum, tijd, bewerking_id, organisatie_id
            )
        else:
            self._metadata = None
        super(Huisnummer, self).__init__(**kwargs)

    @property
    @check_lazy_load_huisnummer
    def straat(self):
        res = self.gateway.get_straat_by_id(self._straat_id)
        return res

    @property
    @check_lazy_load_huisnummer
    def huisnummer(self):
        return self._huisnummer

    @property
    @check_lazy_load_huisnummer
    def metadata(self):
        return self._metadata

    @property
    @check_lazy_load_huisnummer
    def status(self):
        res = self.gateway.list_statushuisnummers()
        for r in res:
            if int(r.id) == int(self._status_id):
                return r

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
    def gebouwen(self):
        return self.gateway.list_gebouwen_by_huisnummer(self.id)

    def __str__(self):
        if self._huisnummer is not None and self.straat is not None:
            return "%s %s" % (self.straat.label, self._huisnummer)
        else:
            return "Huisnummer %s" % (self.id)

    def __repr__(self):
            return "Huisnummer(%s)" % (self.id)


def check_lazy_load_postkanton(f):
    '''
    Decorator function to lazy load a :class:`Postkanton`.
    '''
    def wrapper(*args):
        postkanton = args[0]
        if postkanton._metadata is None:
            postkanton.check_gateway()
            p = postkanton.gateway.get_postkanton_by_huisnummer(postkanton.huisnummer)
            postkanton._metadata = p._metadata
        return f(*args)
    return wrapper


class Postkanton(GatewayObject):
    '''
    A postal code.

    Eg. postal code `9000` for the city of Ghent.
    '''
    def __init__(
        self, id, gemeente_id, datum=None, tijd=None,
        bewerking_id=None, organisatie_id=None, **kwargs
    ):
        self.id = int(id)
        self._gemeente = Gemeente(gemeente_id)
        if (
            datum is not None and tijd is not None and
            bewerking_id is not None and organisatie_id is not None
        ):
            self._metadata = Metadata(
                datum, tijd, bewerking_id, organisatie_id
            )
        else:
            self._metadata = None
        super(Postkanton, self).__init__(**kwargs)

    @property
    @check_lazy_load_postkanton
    def metadata(self):
        return self._metadata

    @property
    def gemeente(self):
        return self._gemeente

    @property
    def huisnummer(self):
        gemeente = self._gemeente
        straat = self.gateway.list_straten(gemeente)[0]
        huisnummer = self.gateway.list_huisnummers_by_straat(straat)[0]
        return huisnummer

    def __str__(self):
        return "Postkanton %s" % (self.id)

    def __repr__(self):
        return "Postkanton(%s)" % (self.id)


def check_lazy_load_wegobject(f):
    '''
    Decorator function to lazy load a :class:`Wegobject`.
    '''
    def wrapper(*args):
        wegobject = args[0]
        if (
            wegobject._aard_id is None or wegobject._centroid is None or
            wegobject._bounding_box is None or
            wegobject._metadata is None
        ):
            wegobject.check_gateway()
            w = wegobject.gateway.get_wegobject_by_id(wegobject.id)
            wegobject._aard_id = w._aard_id
            wegobject._centroid = w._centroid
            wegobject._bounding_box = w._bounding_box
            wegobject._metadata = w._metadata
        return f(*args)
    return wrapper


class Wegobject(GatewayObject):
    def __init__(
        self, id, aard_id=None, centroid=None,
        bounding_box=None, datum=None, tijd=None,
        bewerking_id=None, organisatie_id=None,  **kwargs
    ):
        self.id = id
        self._aard_id = aard_id
        self._centroid = centroid
        self._bounding_box = bounding_box
        if (
            datum is not None and tijd is not None and
            bewerking_id is not None and organisatie_id is not None
        ):
            self._metadata = Metadata(
                datum, tijd, bewerking_id, organisatie_id
            )
        else:
            self._metadata = None
        super(Wegobject, self).__init__(**kwargs)

    @property
    @check_lazy_load_wegobject
    def aard(self):
        res = self.gateway.list_aardwegobjecten()
        for r in res:
            if int(r.id) == int(self._aard_id):
                return r

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

    def __str__(self):
        return "Wegobject %s" % (self.id)

    def __repr__(self):
        return "Wegobject(%s)" % (self.id)


def check_lazy_load_wegsegment(f):
    '''
    Decorator function to lazy load a :class:`Wegsegment`.
    '''
    def wrapper(*args):
        wegsegment = args[0]
        if (
            wegsegment._status_id is None or wegsegment._methode_id
            is None or wegsegment._geometrie is None or
            wegsegment._metadata is None
        ):
            wegsegment.check_gateway()
            w = wegsegment.gateway.get_wegsegment_by_id(wegsegment.id)
            wegsegment._status_id = w._status_id
            wegsegment._methode_id = w._methode_id
            wegsegment._geometrie = w._geometrie
            wegsegment._metadata = w._metadata
        return f(*args)
    return wrapper


class Wegsegment(GatewayObject):
    def __init__(
        self, id, status_id=None, methode_id=None,
        geometrie=None, datum=None, tijd=None,
        bewerking_id=None, organisatie_id=None, **kwargs
    ):
        self.id = id
        self._status_id = status_id
        self._methode_id = methode_id
        self._geometrie = geometrie
        if (
            datum is not None and tijd is not None and
            bewerking_id is not None and organisatie_id is not None
        ):
            self._metadata = Metadata(
                datum, tijd, bewerking_id, organisatie_id
            )
        else:
            self._metadata = None
        super(Wegsegment, self).__init__(**kwargs)

    @property
    @check_lazy_load_wegsegment
    def status(self):
        res = self.gateway.list_statuswegsegmenten()
        for r in res:
            if int(r.id) == int(self._status_id):
                return r

    @property
    @check_lazy_load_wegsegment
    def methode(self):
        res = self.gateway.list_geometriemethodewegsegmenten()
        for r in res:
            if int(r.id) == int(self._methode_id):
                return r

    @property
    @check_lazy_load_wegsegment
    def geometrie(self):
        return self._geometrie

    @property
    @check_lazy_load_wegsegment
    def metadata(self):
        return self._metadata

    def __str__(self):
        return "Wegsegment %s" % (self.id)

    def __repr__(self):
        return "Wegsegment(%s)" % (self.id)


def check_lazy_load_terreinobject(f):
    '''
    Decorator function to lazy load a :class:`Terreinobject`.
    '''
    def wrapper(*args):
        terreinobject = args[0]
        if (
            terreinobject._aard_id is None or terreinobject._centroid
            is None or terreinobject._bounding_box is None or
            terreinobject._metadata is None
        ):
            terreinobject.check_gateway()
            t = terreinobject.gateway.get_terreinobject_by_id(terreinobject.id)
            terreinobject._aard_id = t._aard_id
            terreinobject._centroid = t._centroid
            terreinobject._bounding_box = t._bounding_box
            terreinobject._metadata = t._metadata
        return f(*args)
    return wrapper


class Terreinobject(GatewayObject):
    '''
    A cadastral parcel.

    A :class:`Terreinobject` is somewhat different from a :class:`Perceel`
    in the source of the data and the information provided. eg. A 
    `terreinobject` has a `centroid` and a `bounding box`, while a `perceel`
    also has the centroid, but not the `bounding box`.
    '''
    def __init__(
        self, id, aard_id=None, centroid=None,
        bounding_box=None, datum=None, tijd=None,
        bewerking_id=None, organisatie_id=None,  **kwargs
    ):
        self.id = id
        self._aard_id = aard_id
        self._centroid = centroid
        if (
            datum is not None and tijd is not None and
            bewerking_id is not None and organisatie_id is not None
        ):
            self._metadata = Metadata(
                datum, tijd, bewerking_id, organisatie_id
            )
        else:
            self._metadata = None
        self._bounding_box = bounding_box

    @property
    @check_lazy_load_terreinobject
    def aard(self):
        res = self.gateway.list_aardterreinobjecten()
        for r in res:
            if int(r.id) == int(self._aard_id):
                return r

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

    def __str__(self):
        return "Terreinobject %s" % (self.id)

    def __repr__(self):
        return "Terreinobject(%s)" % (self.id)


def check_lazy_load_perceel(f):
    '''
    Decorator function to lazy load a :class:`Perceel`.
    '''
    def wrapper(*args):
        perceel = args[0]
        if perceel._centroid is None or perceel._metadata is None:
            perceel.check_gateway()
            p = perceel.gateway.get_perceel_by_id(perceel.id)
            perceel._centroid = p._centroid
            perceel._metadata = p._metadata
        return f(*args)
    return wrapper


class Perceel(GatewayObject):
    '''
    A cadastral Parcel.

    A :class:`Terreinobject` is somewhat different from a :class:`Perceel`
    in the source of the data and the information provided. eg. A 
    `terreinobject` has a `centroid` and a `bounding box`, while a `perceel`
    also has the centroid, but not the `bounding box`.
    '''
    def __init__(
        self, id, centroid=None, datum=None, tijd=None,
        bewerking_id=None, organisatie_id=None, **kwargs
    ):
        self.id = id
        self._centroid = centroid
        if (
            datum is not None and tijd is not None and
            bewerking_id is not None and organisatie_id is not None
        ):
            self._metadata = Metadata(
                datum, tijd, bewerking_id, organisatie_id
            )
        else:
            self._metadata = None
        super(Perceel, self).__init__(**kwargs)

    @property
    @check_lazy_load_perceel
    def centroid(self):
        return self._centroid

    @property
    @check_lazy_load_perceel
    def metadata(self):
        return self._metadata

    def __str__(self):
        return "Perceel %s" % (self.id)

    def __repr__(self):
        return "Perceel(%s)" % (self.id)


def check_lazy_load_gebouw(f):
    '''
    Decorator function to lazy load a :class:`Gebouw`.
    '''
    def wrapper(*args):
        gebouw = args[0]
        if (
            gebouw._aard_id is None or gebouw._status_id is None or
            gebouw._methode_id is None or gebouw._geometrie is None or
            gebouw._metadata is None
        ):
            gebouw.check_gateway()
            g = gebouw.gateway.get_gebouw_by_id(gebouw.id)
            gebouw._aard_id = g._aard_id
            gebouw._status_id = g._status_id
            gebouw._methode_id = g._methode_id
            gebouw._geometrie = g._geometrie
            gebouw._metadata = g._metadata
        return f(*args)
    return wrapper


class Gebouw(GatewayObject):
    '''
    A building.
    '''
    def __init__(
        self, id, aard_id=None, status_id=None,
        methode_id=None, geometrie=None, datum=None,
        tijd=None, bewerking_id=None, organisatie_id=None, **kwargs
    ):
        self.id = int(id)
        self._aard_id = aard_id
        self._status_id = status_id
        self._methode_id = methode_id
        self._geometrie = geometrie
        if (
            datum is not None and tijd is not None and bewerking_id
            is not None and organisatie_id is not None
        ):
            self._metadata = Metadata(
                datum, tijd, bewerking_id, organisatie_id
            )
        else:
            self._metadata = None
        super(Gebouw, self).__init__(**kwargs)

    @property
    @check_lazy_load_gebouw
    def aard(self):
        self.check_gateway()
        res = self.gateway.list_aardgebouwen()
        for r in res:
            if int(r.id) == int(self._aard_id):
                return r

    @property
    @check_lazy_load_gebouw
    def status(self):
        res = self.gateway.list_statusgebouwen()
        for r in res:
            if int(r.id) == int(self._status_id):
                return r

    @property
    @check_lazy_load_gebouw
    def methode(self):
        res = self.gateway.list_geometriemethodegebouwen()
        for r in res:
            if int(r.id) == int(self._methode_id):
                return r

    @property
    @check_lazy_load_gebouw
    def geometrie(self):
        return self._geometrie

    @property
    @check_lazy_load_gebouw
    def metadata(self):
        return self._metadata

    def __str__(self):
        return "Gebouw %s" % (self.id)

    def __repr__(self):
        return "Gebouw(%s)" % (self.id)


class Metadata(GatewayObject):
    '''
    Metadata about a `straat`, `huisnummer`, ...

    Some of the metadata available is the datum the object was created, the
    organisation that created it and the type of creation.
    '''
    def __init__(
        self, begin_datum, begin_tijd,
        begin_bewerking_id, begin_organisatie_id
    ):
        self.begin_datum = str(begin_datum)
        self.begin_tijd = str(begin_tijd)
        self._begin_bewerking_id = begin_bewerking_id
        self._begin_organisatie_id = begin_organisatie_id

    @property
    def begin_bewerking(self):
        self.check_gateway()
        res = self.gateway.list_bewerkingen()
        for r in res:
            if int(r.id) == int(self._begin_bewerking_id):
                return r

    @property
    def begin_organisatie(self):
        res = self.gateway.list_organisaties()
        for r in res:
            if int(r.id) == int(self._begin_organisatie_id):
                return r
