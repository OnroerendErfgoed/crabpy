from crabpy.client import capakey_request

class CapakeyGateway(object):

    def __init__(self, client):
        self.client = client

    def list_gemeenten(self, sort=1):
        res = capakey_request(self.client, 'ListAdmGemeenten', sort)
        return [Gemeente(r.Niscode, r.AdmGemeentenaam, gateway=self) for r in res.AdmGemeenteItem]

    def get_gemeente_by_id(self, id):
        res = capakey_request(self.client, 'GetAdmGemeenteByNiscode', id)
        return Gemeente(
            res.Niscode,
            res.AdmGemeentenaam,
            (res.CenterX, res.CenterY),
            (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY),
            gateway=self
        )

    def list_kadastrale_afdelingen(self, sort=1):
        res = capakey_request(self.client, 'ListKadAfdelingen', sort)
        return [
            Afdeling(
                r.KadAfdelingcode,
                r.KadAfdelingnaam,
                Gemeente(r.Niscode, gateway=self),
                gateway=self
            ) for r in res.KadAfdelingItem]

    def list_kadastrale_afdelingen_by_gemeente(self, gemeente, sort=1):
        try:
            gid = gemeente.id
        except AttributeError:
            gemeente = self.get_gemeente_by_id(gemeente)
            gid = gemeente.id
        res = capakey_request(self.client, 'ListKadAfdelingenByNiscode', gid, sort)
        return [
            Afdeling(
                r.KadAfdelingcode,
                r.KadAfdelingnaam,
                gemeente,
                gateway=self
            ) for r in res.KadAfdelingItem]

    def get_kadastrale_afdeling_by_id(self, id):
        res = capakey_request(self.client, 'GetKadAfdelingByKadAfdelingcode', id)
        return Afdeling(
            id=res.KadAfdelingcode,
            naam=res.KadAfdelingnaam,
            gemeente=Gemeente(res.Niscode, res.AdmGemeentenaam, gateway=self),
            centroid=(res.CenterX, res.CenterY),
            bounding_box=(res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY),
            gateway=self
        )

    def list_secties_by_afdeling(self, afdeling):
        try:
            aid = afdeling.id
        except AttributeError:
            afdeling = self.get_kadastrale_afdeling_by_id(afdeling)
            aid = afdeling.id
        res = capakey_request(self.client, 'ListKadSectiesByKadAfdelingcode', aid)
        return [
            Sectie(
                r.KadSectiecode,
                afdeling,
                gateway=self
            ) for r in res.KadSectieItem
        ]
    
    def get_sectie_by_id_and_afdeling(self, id, afdeling):
        try:
            aid = afdeling.id
        except AttributeError:
            afdeling = self.get_kadastrale_afdeling_by_id(afdeling)
            aid = afdeling.id
        res = capakey_request(self.client, 'GetKadSectieByKadSectiecode', aid, id)
        return Sectie(
            res.KadSectiecode,
            afdeling,
            (res.CenterX, res.CenterY),
            (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY),
            gateway=self
        )

    def list_percelen_by_sectie(self, sectie, sort=1):
        res = capakey_request(self.client, 'ListKadPerceelsnummersByKadSectiecode', sectie.afdeling.id, sectie.id, sort)
        return [
            Perceel(
                r.KadPerceelsnummer,
                sectie,
                r.CaPaKey,
                r.PERCID,
            ) for r in res.KadPerceelsnummerItem
        ]

    def get_perceel_by_id_and_sectie(self, id, sectie):
        res = capakey_request(self.client, 'GetKadPerceelsnummerByKadPerceelsnummer', sectie.afdeling.id, sectie.id, id)
        return Perceel(
            res.KadPerceelsnummer,
            sectie,
            res.CaPaKey,
            res.PERCID,
            res.CaPaTy,
            res.CaShKey,
            (res.CenterX, res.CenterY),
            (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY),
            gateway=self
        )

    def get_perceel_by_capakey(self, capakey):
        res = capakey_request(self.client, 'GetKadPerceelsnummerByCaPaKey', capakey)
        afdeling = Afdeling(res.KadAfdelingcode, gateway=self)
        sectie = Sectie(res.KadSectiecode, afdeling, gateway=self)
        return Perceel(
            res.KadPerceelsnummer,
            sectie,
            res.CaPaKey,
            res.PERCID,
            res.CaPaTy,
            res.CaShKey,
            (res.CenterX, res.CenterY),
            (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY),
            gateway=self
        )

    def get_perceel_by_percid(self, percid):
        res = capakey_request(self.client, 'GetKadPerceelsnummerByPERCID', percid)
        afdeling = Afdeling(res.KadAfdelingcode, gateway=self)
        sectie = Sectie(res.KadSectiecode, afdeling, gateway=self)
        return Perceel(
            res.KadPerceelsnummer,
            sectie,
            res.CaPaKey,
            res.PERCID,
            res.CaPaTy,
            res.CaShKey,
            (res.CenterX, res.CenterY),
            (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY),
            gateway=self
        )


class GatewayObject(object):

    gateway = None

    def __init__(self, **kwargs):
        if 'gateway' in kwargs:
            self.set_gateway(kwargs['gateway'])

    def set_gateway(self, gateway):
        self.gateway = gateway

    def check_gateway(self):
        if not self.gateway:
            raise RuntimeError("There's no Gateway I can use")


def check_lazy_load_gemeente(f):
    def wrapper(*args):
        gemeente = args[0]
        if gemeente._naam is None or gemeente._centroid is None or gemeente._bounding_box is None:
            gemeente.check_gateway()
            g = gemeente.gateway.get_gemeente_by_id(gemeente.id)
            gemeente._naam = g._naam
            gemeente._centroid = g._centroid
            gemeente._bounding_box = g._bounding_box
        return f(*args)
    return wrapper


class Gemeente(GatewayObject):

    def __init__(
            self, id, naam=None, 
            centroid=None, bounding_box=None,
            **kwargs):
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

    def __str__(self):
        return '%s (%s)' % (self.naam, self.id)


def check_lazy_load_afdeling(f):
    def wrapper(*args):
        afdeling = args[0]
        if afdeling._naam is None or afdeling._gemeente is None or afdeling._centroid is None or afdeling._bounding_box is None:
            afdeling.check_gateway()
            a = afdeling.gateway.get_kadastrale_afdeling_by_id(afdeling.id)
            afdeling._naam = a._naam
            afdeling._gemeente = a._gemeente
            afdeling._centroid = a._centroid
            afdeling._bounding_box = a._bounding_box
        return f(*args)
    return wrapper


class Afdeling(GatewayObject):

    def __init__(
        self, id, naam=None, gemeente=None,
        centroid=None, bounding_box=None,
        **kwargs):
        self.id = int(id)
        self._naam = naam
        self._gemeente = gemeente
        self._centroid = centroid
        self._bounding_box = bounding_box
        super(Afdeling, self).__init__(**kwargs)

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

    def __str__(self):
        if self._naam is not None:
            return '%s (%s)' % (self._naam, self.id)
        else:
            return 'Afdeling %s' % (self.id)

def check_lazy_load_sectie(f):
    def wrapper(*args):
        sectie = args[0]
        if sectie._centroid is None or sectie._bounding_box is None:
            sectie.check_gateway()
            s = sectie.gateway.get_sectie_by_id_and_afdeling(sectie.id, sectie.afdeling.id)
            sectie._centroid = s._centroid
            sectie._bounding_box = s._bounding_box
        return f(*args)
    return wrapper


class Sectie(GatewayObject):

    def __init__(
        self, id, afdeling,
        centroid=None, bounding_box=None,
        **kwargs):
        self.id = id
        self.afdeling = afdeling
        self._centroid = centroid
        self._bounding_box = bounding_box
        super(Sectie, self).__init__(**kwargs)

    @property
    @check_lazy_load_sectie
    def centroid(self):
        return self._centroid

    @property
    @check_lazy_load_sectie
    def bounding_box(self):
        return self._bounding_box

    def __str__(self):
        return '%s, Sectie %s' % (self.afdeling, self.id)


def check_lazy_load_perceel(f):
    def wrapper(*args):
        perceel = args[0]
        if perceel._capatype is None or perceel._cashkey is None\
        or perceel._centroid is None or perceel._bounding_box is None:
            perceel.check_gateway()
            p = perceel.gateway.get_perceel_by_id_and_sectie(perceel.id, perceel.sectie)
            perceel._centroid = p._centroid
            perceel._bounding_box = p._bounding_box
        return f(*args)
    return wrapper

class Perceel(GatewayObject):

    def __init__(
        self, id, sectie, capakey, percid,
        capatype=None, cashkey=None,
        centroid=None, bounding_box=None,
        **kwargs):
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

    def _split_capakey(self):
        import re
        match = re.match(
            r"^[0-9]{5}[A_Z]{1}([0-9]{4})\/([0-9]{2})([A-Z\_]{1})([0-9]{3})$",
            self.capakey
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

    def __str__(self):
        return self.capakey
