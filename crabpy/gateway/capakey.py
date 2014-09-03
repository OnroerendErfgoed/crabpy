# -*- coding: utf-8 -*-
'''
This module contains an opionated gateway for the capakey webservice.

.. versionadded:: 0.2.0
'''

from __future__ import unicode_literals
import six

import logging
log = logging.getLogger(__name__)

from crabpy.client import capakey_request

from suds import WebFault

from crabpy.gateway.exception import (
    GatewayRuntimeException,
    GatewayAuthenticationException
)

from dogpile.cache import make_region


def capakey_gateway_request(client, method, *args):
    '''
    Utility function that helps making requests to the CAPAKEY service.

    This is a specialised version of :func:`crabpy.client.capakey_request` that
    allows adding extra functionality like general error handling for the
    calls made by the gateway.

    :param client: A :class:`suds.client.Client` for the CAPAKEY service.
    :param string action: Which method to call, eg. `ListAdmGemeenten`.
    :returns: Result of the SOAP call.
    '''
    try:
        return capakey_request(client, method, *args)
    except WebFault as wf:
        if wf.fault['faultcode'] == 'q0:FailedAuthentication':
            err = GatewayAuthenticationException(
                'Could not authenticate with capakey service. Message from server:\n%s' % wf.fault['faultstring'],
                wf
            )
        else:
            err = GatewayRuntimeException(
                'Could not execute request. Message from server:\n%s' % wf.fault['faultstring'],
                wf
            )
        raise err


class CapakeyGateway(object):
    '''
    A gateway to the capakey webservice.
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
                    log.debug('Configuring %s region on CapakeyGateway', cr)
                    self.caches[cr].configure_from_config(
                        kwargs['cache_config'],
                        '%s.' % cr
                    )

    def list_gemeenten(self, sort=1):
        '''
        List all `gemeenten` in Vlaanderen.

        :param integer sort: What field to sort on.
        :rtype: A :class:`list` of :class:`Gemeente`.
        '''
        def creator():
            res = capakey_gateway_request(
                self.client, 'ListAdmGemeenten', sort
            )
            return [
                Gemeente(r.Niscode, r.AdmGemeentenaam)
                for r in res.AdmGemeenteItem
            ]
        if self.caches['permanent'].is_configured:
            key = 'ListAdmGemeenten#%s' % sort
            gemeente = self.caches['permanent'].get_or_create(key, creator)
        else:
            gemeente = creator()
        for g in gemeente:
            g.set_gateway(self)
        return gemeente

    def get_gemeente_by_id(self, id):
        '''
        Retrieve a `gemeente` by id (the NIScode).

        :rtype: :class:`Gemeente`
        '''
        def creator():
            res = capakey_gateway_request(
                self.client, 'GetAdmGemeenteByNiscode', id
            )
            return Gemeente(
                res.Niscode,
                res.AdmGemeentenaam,
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY)
            )
        if self.caches['long'].is_configured:
            key = 'GetAdmGemeenteByNiscode#%s' % id
            gemeente = self.caches['long'].get_or_create(key, creator)
        else:
            gemeente = creator()
        gemeente.set_gateway(self)
        return gemeente

    def list_kadastrale_afdelingen(self, sort=1):
        '''
        List all `kadastrale afdelingen` in Flanders.

        :param integer sort: Field to sort on.
        :rtype: A :class:`list` of :class:`Afdeling`.
        '''
        def creator():
            res = capakey_gateway_request(
                self.client, 'ListKadAfdelingen', sort
            )
            return [
                Afdeling(
                    id=r.KadAfdelingcode,
                    naam=r.KadAfdelingnaam,
                    gemeente=Gemeente(r.Niscode)
                ) for r in res.KadAfdelingItem]
        if self.caches['permanent'].is_configured:
            key = 'ListKadAfdelingen#%s' % sort
            afdelingen = self.caches['permanent'].get_or_create(key, creator)
        else:
            afdelingen = creator()
        for a in afdelingen:
            a.set_gateway(self)
        return afdelingen

    def list_kadastrale_afdelingen_by_gemeente(self, gemeente, sort=1):
        '''
        List all `kadastrale afdelingen` in a `gemeente`.

        :param gemeente: The :class:`Gemeente` for which the \
            `afdelingen` are wanted.
        :param integer sort: Field to sort on.
        :rtype: A :class:`list` of :class:`Afdeling`.
        '''
        try:
            gid = gemeente.id
        except AttributeError:
            gid = gemeente
            gemeente = self.get_gemeente_by_id(gid)
        gemeente.clear_gateway()

        def creator():
            res = capakey_gateway_request(
                self.client, 'ListKadAfdelingenByNiscode', gid, sort
            )
            return [
                Afdeling(
                    id=r.KadAfdelingcode,
                    naam=r.KadAfdelingnaam,
                    gemeente=gemeente
                ) for r in res.KadAfdelingItem]
        if self.caches['permanent'].is_configured:
            key = 'ListKadAfdelingenByNiscode#%s#%s' % (gid, sort)
            afdelingen = self.caches['permanent'].get_or_create(key, creator)
        else:
            afdelingen = creator()
        for a in afdelingen:
            a.set_gateway(self)
        return afdelingen

    def get_kadastrale_afdeling_by_id(self, id):
        '''
        Retrieve a 'kadastrale afdeling' by id.

        :param id: An id of a `kadastrale afdeling`.
        :rtype: A :class:`Afdeling`.
        '''
        def creator():
            res = capakey_gateway_request(
                self.client, 'GetKadAfdelingByKadAfdelingcode', id
            )
            return Afdeling(
                id=res.KadAfdelingcode,
                naam=res.KadAfdelingnaam,
                gemeente=Gemeente(res.Niscode, res.AdmGemeentenaam),
                centroid=(res.CenterX, res.CenterY),
                bounding_box=(
                    res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY
                )
            )
        if self.caches['long'].is_configured:
            key = 'GetKadAfdelingByKadAfdelingcode#%s' % id
            afdeling = self.caches['long'].get_or_create(key, creator)
        else:
            afdeling = creator()
        afdeling.set_gateway(self)
        return afdeling

    def list_secties_by_afdeling(self, afdeling):
        '''
        List all `secties` in a `kadastrale afdeling`.

        :param afdeling: The :class:`Afdeling` for which the `secties` are \
            wanted. Can also be the id of and `afdeling`.
        :rtype: A :class:`list` of `Sectie`.
        '''
        try:
            aid = afdeling.id
        except AttributeError:
            aid = afdeling
            afdeling = self.get_kadastrale_afdeling_by_id(aid)
        afdeling.clear_gateway()

        def creator():
            res = capakey_gateway_request(
                self.client, 'ListKadSectiesByKadAfdelingcode', aid
            )
            return [
                Sectie(
                    r.KadSectiecode,
                    afdeling
                ) for r in res.KadSectieItem
            ]
        if self.caches['long'].is_configured:
            key = 'ListKadSectiesByKadAfdelingcode#%s' % aid
            secties = self.caches['long'].get_or_create(key, creator)
        else:
            secties = creator()
        for s in secties:
            s.set_gateway(self)
        return secties

    def get_sectie_by_id_and_afdeling(self, id, afdeling):
        '''
        Get a `sectie`.

        :param id: An id of a sectie. eg. "A"
        :param afdeling: The :class:`Afdeling` for in which the `sectie` can \
            be found. Can also be the id of and `afdeling`.
        :rtype: A :class:`Sectie`.
        '''
        try:
            aid = afdeling.id
        except AttributeError:
            aid = afdeling
            afdeling = self.get_kadastrale_afdeling_by_id(aid)
        afdeling.clear_gateway()

        def creator():
            res = capakey_gateway_request(
                self.client, 'GetKadSectieByKadSectiecode', aid, id
            )
            return Sectie(
                res.KadSectiecode,
                afdeling,
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY),
            )
        if self.caches['long'].is_configured:
            key = 'GetKadSectieByKadSectiecode#%s#%s' % (aid, id)
            sectie = self.caches['long'].get_or_create(key, creator)
        else:
            sectie = creator()
        sectie.set_gateway(self)
        return sectie

    def list_percelen_by_sectie(self, sectie, sort=1):
        '''
        List all percelen in a `sectie`.

        :param sectie: The :class:`Sectie` for which the percelen are wanted.
        :param integer sort: Field to sort on.
        :rtype: A :class:`list` of :class:`Perceel`.
        '''
        sectie.clear_gateway()

        def creator():
            res = capakey_gateway_request(
                self.client, 'ListKadPerceelsnummersByKadSectiecode',
                sectie.afdeling.id, sectie.id, sort
            )
            return [
                Perceel(
                    r.KadPerceelsnummer,
                    sectie,
                    r.CaPaKey,
                    r.PERCID,
                ) for r in res.KadPerceelsnummerItem
            ]
        if self.caches['short'].is_configured:
            key = 'ListKadPerceelsnummersByKadSectiecode#%s#%s#%s' % (sectie.afdeling.id, sectie.id, sort)
            percelen = self.caches['short'].get_or_create(key, creator)
        else:
            percelen = creator()
        for p in percelen:
            p.set_gateway(self)
        return percelen

    def get_perceel_by_id_and_sectie(self, id, sectie):
        '''
        Get a `perceel`.

        :param id: An id for a `perceel`.
        :param sectie: The :class:`Sectie` that contains the perceel.
        :rtype: :class:`Perceel`
        '''
        sectie.clear_gateway()

        def creator():
            res = capakey_gateway_request(
                self.client, 'GetKadPerceelsnummerByKadPerceelsnummer',
                sectie.afdeling.id, sectie.id, id
            )
            return Perceel(
                res.KadPerceelsnummer,
                sectie,
                res.CaPaKey,
                res.PERCID,
                res.CaPaTy,
                res.CaShKey,
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY)
            )
        if self.caches['short'].is_configured:
            key = 'GetKadPerceelsnummerByKadPerceelsnummer#%s#%s#%s' % (sectie.afdeling.id, sectie.id, id)
            perceel = self.caches['short'].get_or_create(key, creator)
        else:
            perceel = creator()
        perceel.set_gateway(self)
        return perceel

    def get_perceel_by_capakey(self, capakey):
        '''
        Get a `perceel`.

        :param capakey: An capakey for a `perceel`.
        :rtype: :class:`Perceel`
        '''
        def creator():
            res = capakey_gateway_request(
                self.client, 'GetKadPerceelsnummerByCaPaKey', capakey
            )
            return Perceel(
                res.KadPerceelsnummer,
                Sectie(res.KadSectiecode, Afdeling(res.KadAfdelingcode)),
                res.CaPaKey,
                res.PERCID,
                res.CaPaTy,
                res.CaShKey,
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY)
            )
        if self.caches['short'].is_configured:
            key = 'GetKadPerceelsnummerByCaPaKey#%s' % capakey
            perceel = self.caches['short'].get_or_create(key, creator)
        else:
            perceel = creator()
        perceel.set_gateway(self)
        return perceel

    def get_perceel_by_percid(self, percid):
        '''
        Get a `perceel`.

        :param percid: A percid for a `perceel`.
        :rtype: :class:`Perceel`
        '''
        def creator():
            res = capakey_gateway_request(
                self.client, 'GetKadPerceelsnummerByPERCID', percid
            )
            return Perceel(
                res.KadPerceelsnummer,
                Sectie(res.KadSectiecode, Afdeling(res.KadAfdelingcode)),
                res.CaPaKey,
                res.PERCID,
                res.CaPaTy,
                res.CaShKey,
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY)
            )
        if self.caches['short'].is_configured:
            key = 'GetKadPerceelsnummerByPERCID#%s' % percid
            perceel = self.caches['short'].get_or_create(key, creator)
        else:
            perceel = creator()
        perceel.set_gateway(self)
        return perceel


class GatewayObject(object):
    '''
    Abstract class for all objects being returned from the Gateway.
    '''

    gateway = None
    '''
    The :class:`crabpy.gateway.capakey.CapakeyGateway` to use when making
    further calls to the Capakey service.
    '''

    def __init__(self, **kwargs):
        if 'gateway' in kwargs:
            self.set_gateway(kwargs['gateway'])

    def set_gateway(self, gateway):
        '''
        :param crabpy.gateway.capakey.CapakeyGateway gateway: Gateway to use.
        '''
        self.gateway = gateway

    def clear_gateway(self):
        '''
        Clear the currently set CapakeyGateway.
        '''
        self.gateway = None

    def check_gateway(self):
        '''
        Check to see if a gateway was set on this object.
        '''
        if not self.gateway:
            raise RuntimeError("There's no Gateway I can use")

    if six.PY2:
        def __str__(self):
            return self.__unicode__().encode('utf-8')
    else:
        def __str__(self):
            return self.__unicode__()


def check_lazy_load_gemeente(f):
    '''
    Decorator function to lazy load a :class:`Gemeente`.
    '''
    def wrapper(self):
        gemeente = self
        if (getattr(gemeente, '_%s' % f.__name__, None) is None):
            log.debug('Lazy loading Gemeente %d', gemeente.id)
            gemeente.check_gateway()
            g = gemeente.gateway.get_gemeente_by_id(gemeente.id)
            gemeente._naam = g._naam
            gemeente._centroid = g._centroid
            gemeente._bounding_box = g._bounding_box
        return f(self)
    return wrapper


class Gemeente(GatewayObject):
    '''
    The smallest administrative unit in Belgium.
    '''

    def __init__(
            self, id, naam=None,
            centroid=None, bounding_box=None,
            **kwargs
    ):
        self.id = int(id)
        self._naam = naam
        self._centroid = centroid
        self._bounding_box = bounding_box
        super(Gemeente, self).__init__(**kwargs)

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
        return '%s (%s)' % (self.naam, self.id)

    def __repr__(self):
        return "Gemeente(%s, '%s')" % (self.id, self.naam)


def check_lazy_load_afdeling(f):
    '''
    Decorator function to lazy load a :class:`Afdeling`.
    '''
    def wrapper(self):
        afdeling = self
        if (getattr(afdeling, '_%s' % f.__name__, None) is None):
            log.debug('Lazy loading Afdeling %d', afdeling.id)
            afdeling.check_gateway()
            a = afdeling.gateway.get_kadastrale_afdeling_by_id(afdeling.id)
            afdeling._naam = a._naam
            afdeling._gemeente = a._gemeente
            afdeling._centroid = a._centroid
            afdeling._bounding_box = a._bounding_box
        return f(self)
    return wrapper


class Afdeling(GatewayObject):
    '''
    A Cadastral Division of a :class:`Gemeente`.
    '''

    def __init__(
        self, id, naam=None, gemeente=None,
        centroid=None, bounding_box=None,
        **kwargs
    ):
        self.id = int(id)
        self._naam = naam
        self._gemeente = gemeente
        self._centroid = centroid
        self._bounding_box = bounding_box
        super(Afdeling, self).__init__(**kwargs)

    def set_gateway(self, gateway):
        '''
        :param crabpy.gateway.capakey.CapakeyGateway gateway: Gateway to use.
        '''
        self.gateway = gateway
        if (self._gemeente is not None):
            self._gemeente.set_gateway(gateway)

    def clear_gateway(self):
        '''
        Clear the currently set CapakeyGateway.
        '''
        self.gateway = None
        if (self._gemeente is not None):
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
            return '%s (%s)' % (self._naam, self.id)
        else:
            return 'Afdeling %s' % (self.id)

    def __repr__(self):
        if self._naam is not None:
            return "Afdeling(%s, '%s')" % (self.id, self._naam)
        else:
            return 'Afdeling(%s)' % (self.id)


def check_lazy_load_sectie(f):
    '''
    Decorator function to lazy load a :class:`Sectie`.
    '''
    def wrapper(self):
        sectie = self
        if (getattr(sectie, '_%s' % f.__name__, None) is None):
            log.debug('Lazy loading Sectie %s in Afdeling %d', sectie.id, sectie.afdeling.id)
            sectie.check_gateway()
            s = sectie.gateway.get_sectie_by_id_and_afdeling(
                sectie.id, sectie.afdeling.id
            )
            sectie._centroid = s._centroid
            sectie._bounding_box = s._bounding_box
        return f(self)
    return wrapper


class Sectie(GatewayObject):
    '''
    A subdivision of a :class:`Afdeling`.
    '''

    def __init__(
        self, id, afdeling,
        centroid=None, bounding_box=None,
        **kwargs
    ):
        self.id = id
        self.afdeling = afdeling
        self._centroid = centroid
        self._bounding_box = bounding_box
        super(Sectie, self).__init__(**kwargs)

    def set_gateway(self, gateway):
        '''
        :param crabpy.gateway.capakey.CapakeyGateway gateway: Gateway to use.
        '''
        self.gateway = gateway
        self.afdeling.set_gateway(gateway)

    def clear_gateway(self):
        '''
        Clear the currently set CapakeyGateway.
        '''
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
        return '%s, Sectie %s' % (self.afdeling, self.id)

    def __repr__(self):
        return "Sectie('%s', %s)" % (self.id, repr(self.afdeling))


def check_lazy_load_perceel(f):
    '''
    Decorator function to lazy load a :class:`Perceel`.
    '''
    def wrapper(self):
        perceel = self
        if (getattr(perceel, '_%s' % f.__name__, None) is None):
            log.debug(
                'Lazy loading Perceel %s in Sectie %s in Afdeling %d',
                perceel.id,
                perceel.sectie.id,
                perceel.sectie.afdeling.id
            )
            perceel.check_gateway()
            p = perceel.gateway.get_perceel_by_id_and_sectie(
                perceel.id,
                perceel.sectie
            )
            perceel._centroid = p._centroid
            perceel._bounding_box = p._bounding_box
            perceel._capatype = p._capatype
            perceel._cashkey = p._cashkey
        return f(self)
    return wrapper


class Perceel(GatewayObject):
    '''
    A Cadastral Parcel.
    '''

    def __init__(
        self, id, sectie, capakey, percid,
        capatype=None, cashkey=None,
        centroid=None, bounding_box=None,
        **kwargs
    ):
        self.id = id
        self.sectie = sectie
        self.capakey = capakey
        self.percid = percid
        self._capatype = capatype
        self._cashkey = cashkey
        self._centroid = centroid
        self._bounding_box = bounding_box
        super(Perceel, self).__init__(**kwargs)
        self._split_capakey()

    def set_gateway(self, gateway):
        '''
        :param crabpy.gateway.capakey.CapakeyGateway gateway: Gateway to use.
        '''
        self.gateway = gateway
        self.sectie.set_gateway(gateway)

    def clear_gateway(self):
        '''
        Clear the currently set CapakeyGateway.
        '''
        self.gateway = None
        self.sectie.clear_gateway()

    def _split_capakey(self):
        '''
        Split a capakey into more readable elements.

        Splits a capakey into it's grondnummer, bisnummer, exponent and macht.
        '''
        import re
        match = re.match(
            r"^[0-9]{5}[A-Z]{1}([0-9]{4})\/([0-9]{2})([A-Z\_]{1})([0-9]{3})$",
            self.capakey
        )
        if match:
            self.grondnummer = match.group(1)
            self.bisnummer = match.group(2)
            self.exponent = match.group(3)
            self.macht = match.group(4)
        else:
            raise ValueError(
                "Invalid Capakey %s can't be parsed" % self.capakey
            )

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
        return "Perceel('%s', %s, '%s', '%s')" % (
            self.id, repr(self.sectie), self.capakey, self.percid
        )
