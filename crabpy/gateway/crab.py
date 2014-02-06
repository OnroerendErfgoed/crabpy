# -*- coding: utf-8 -*-

from crabpy.client import crab_request

from suds import WebFault

from crabpy.gateway.exception import (
    GatewayRuntimeException
)

from dogpile.cache import make_region



def crab_gateway_request(client, method, *args):
    try:
        return crab_request(client, method, *args)
    except WebFault as wf:
        err=GatewayRuntimeException(
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
        List all `gewesten`
        
        :param integer sort: What field to sort on.
        :rtype: A :class`list` of class: `Gewest`.
        '''
        
        def creator():
            res=crab_gateway_request(self.client,'ListGewesten',sort)
            return[
                Gewest(
                    r.GewestId,
                    r.GewestNaam,
                    gateway=self
                )for r in res.GewestItem
            ]

        if self.caches['long'].is_configured:
            key='ListGewesten#%s' %sort
            return self.caches['permanent'].get_or_create(key,creator)
        else:
            return creator()

    def list_gemeenten(self, gewest=2, sort=1):
        '''
        List all `gemeenten` in a `gewest`.

        :param integer gewest: What gewest to list the `gemeenten` for.
        :param integer sort: What field to sort on.
        :rtype: A :class:`list` of :class:`Gemeente`.
        '''
        
        def creator():
            res= crab_gateway_request(self.client,'ListGemeentenByGewestId', gewest ,sort)
            return[ 
                Gemeente(
                    r.GemeenteId,
                    r.GemeenteNaam,
                    r.NISGemeenteCode,
                    gateway=self
                )for r in res.GemeenteItem
            ]
        if self.caches['long'].is_configured:
            key='ListGemeentenByGewestId#%s%s'%(gewest, sort)
            return self.caches['long'].get_or_create(key, creator)
        else:
            return creator()

    def get_gemeente_by_id(self, id):
        '''
        Retrieve a `gemeente` by the crab id.

        :param integer id: The CRAB id of the gemeente.
        :rtype: :class:`Gemeente`
        '''
        
        def creator():  
            res=crab_gateway_request(self.client, 'GetGemeenteByGemeenteId', id)
            return Gemeente(
                res.GemeenteId,
                res.GemeenteNaam,
                res.NisGemeenteCode,
                res.GewestId,
                res.TaalCode,
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY)
            )
        if self.caches['long'].is_configured:
            key='GetGemeenteByGemeenteId#%s' %id
            gemeente=self.caches['long'].get_or_create(key, creator)
        else:
            gemeente= creator()
        gemeente.set_gateway(self)
        return gemeente
        

    def get_gemeente_by_niscode(self, niscode):
        '''
        Retrieve a `gemeente` by the NIScode.

        :param integer id: The NIScode of the gemeente.
        :rtype: :class:`Gemeente`
        '''
        
        def creator():
            res=crab_gateway_request(self.client, 'GetGemeenteByNISGemeenteCode', niscode)
            return Gemeente(
                res.GemeenteId,
                res.GemeenteNaam,
                res.NisGemeenteCode,
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinimumY, res.MaximumX, res.MaximumY)
            )
        if self.caches['long'].is_configured:
            key='GetGemeenteByNISGemeenteCode#%s' %niscode
            gemeente=self.caches['long'].get_or_create(key, creator)
        else:
            gemeente=creator()
        gemeente.set_gateway(self)
        return gemeente
    
    def _list_codeobject(self, function, sort, returnclass):
        
        def creator():
            res=crab_gateway_request(self.client, function, sort)
            return[
                globals()[returnclass](
                    r.Code,
                    r.Naam,
                    r.Definitie,
                    gateway=self
                )for r in res.CodeItem
            ]
        if self.caches['permanent'].is_configured:
            key=function+'#%s'%(sort)
            return self.caches['permanent'].get_or_create(key, creator)
        else:
            return creator()
        
    def list_talen(self, sort=1):
        '''
        List all `talen`.
        :rtype: A :class:`list` of :class: `Taal`
        '''
        return self._list_codeobject('ListTalen',sort,'Taal')
    
    def list_bewerkingen(self, sort=1):
        '''
        List all `bewerkingen`.
        :rtype: A :class:`list` of :class: `Bewerking`
        '''
        return self._list_codeobject('ListBewerkingen',sort,'Bewerking')
        
    def list_organisaties(self, sort=1):
        '''
        List all `organisaties`.
        :rtype: A :class:`list` of :class: `Organisatie`
        '''
        return self._list_codeobject('ListOrganisaties',sort,'Organisatie')

    def list_aardsubadressen(self, sort=1):
        '''
        List all `aardsubadressen`.
        :rtype: A :class:`list` of :class: `Aardsubadres`
        '''
        return self._list_codeobject('ListOrganisaties',sort, 'Aardsubadres')
        
    def list_aardadressen(self, sort=1):
        '''
        List all `aardadressen`.
        :rtype: A :class:`list` of :class: `Aardadres`
        '''
        return self._list_codeobject('ListAardAdressen',sort,'Aardadres')
        
        
    def list_aardgebouwen(self, sort=1):
        '''
        List all `aardgebouwen`.
        :rtype: A :class:`list` of :class: `Aardgebouw`
        '''
        return self._list_codeobject('ListAardGebouwen',sort,'Aardgebouw')
        
    def list_aardwegobjecten(self, sort=1):
        '''
        List all `aardwegobjecten`.
        :rtype: A :class:`list` of :class: `Aardwegobject`
        '''
        return self._list_codeobject('ListAardWegobjecten',sort,'Aardwegobject')
        
    def list_aardterreinobjecten(self, sort=1):
        '''
        List all `aardterreinobjecten`.
        :rtype: A :class:`list` of :class: `Aardterreinobject`
        '''
        return self._list_codeobject('ListAardTerreinobjecten',sort,'Aardterreinobject')
        
    def list_statushuisnummers(self, sort=1):
        '''
        List all `statushuisnummers`.
        :rtype: A :class:`list` of :class: `Statushuisnummer`
        '''
        return self._list_codeobject('ListStatusHuisnummers',sort,'Statushuisnummer')
        
    def list_statussubadressen(self, sort=1):
        '''
        List all `statussubadressen`.
        :rtype: A :class:`list` of :class: `Statussubadres`
        '''
        return self._list_codeobject('ListStatusSubadressen',sort,'Statussubadres')
       
    def list_statusstraatnamen(self, sort=1):
        '''
        List all `statusstraatnamen`.
        :rtype: A :class:`list` of :class: `Statusstraatnaam`
        '''
        return self._list_codeobject('ListStatusStraatnamen',sort,'Statusstraatnaam')
        
    def list_statuswegsegmenten(self, sort=1):
        '''
        List all `statuswegsegmenten`.
        :rtype: A :class:`list` of :class: `Statuswegsegment`
        '''
        return self._list_codeobject('ListStatusWegsegmenten',sort,'Statuswegsegment')
        
    def list_geometriemethodewegsegmenten(self, sort=1):
        '''
        List all `geometriemethodewegsegmenten`.
        :rtype: A :class:`list` of :class: `Geometriemethodewegsegment`
        '''
        return self._list_codeobject('ListGeometriemethodeWegsegmenten',sort,'Geometriemethodewegsegment')
        
    def list_statusgebouwen(self, sort=1):
        '''
        List all `statusgebouwen`.
        :rtype: A :class:`list` of :class: `Statusgebouwen`
        '''
        return self._list_codeobject('ListStatusGebouwen',sort,'Statusgebouw')
        
    def list_geometriemethodegebouwen(self, sort=1):
        '''
        List all `geometriegebouwen`.
        :rtype: A :class:`list` of :class: `Geometriegebouw`
        '''
        return self._list_codeobject('ListGeometriemethodeGebouwen',sort,'Geometriemethodegebouw')
        
    def list_herkomstadresposities(self, sort=1):
        '''
        List all `herkomstadresposities`.
        :rtype: A :class:`list` of :class: `Herkomstadrespositie`
        '''
        return self._list_codeobject('ListHerkomstAdresposities',sort,'Herkomstadrespositie')
        
    def list_straten(self, gemeente, sort=1):
        '''
        List all `straten` in a `Gemeente`.

        :param object gemeente: An object of :class: `Gemeente`
        :rtype: A :class:`list` of :class: `Straat`
        '''
        def creator():
            res=crab_gateway_request(self.client, 'ListStraatnamenWithStatusByGemeenteId', gemeente, sort)
            return[ 
                Straat(
                    r.StraatnaamId,
                    r.StraatnaamLabel,
                    r.StatusStraatnaam,
                    gateway=self
                )for r in res.StraatnaamWithStatusItem
            ]
        if self.caches['long'].is_configured:
            key='ListStraatnamenWithStatusByGemeenteId#%s%s'%(gemeente, sort)
            return self.caches['long'].get_or_create(key, creator)
        else:
            return creator()
        
    def get_straat_by_id(self,id):
        '''
        Retrieve a `straat`by the Id.
         
        :param integer id: The id of the `straat`.
        :rtype: :class:`Straat`
        '''
        def creator():
            res=crab_gateway_request(self.client, 'GetStraatnaamWithStatusByStraatnaamId', id)
            return Straat(
                    res.StraatnaamId,
                    res.StraatnaamLabel,
                    res.StatusStraatnaam,
                    res.Straatnaam,
                    res.TaalCode,
                    res.StraatnaamTweedeTaal,
                    res.TaalCodeTweedeTaal,
                    res.GemeenteId,
            )

        if self.caches['long'].is_configured:
            key='GetStraatnaamWithStatusByStraatnaamId#%s'%(id)
            straat=self.caches['long'].get_or_create(key, creator)
        else:
            straat=creator()
        straat.set_gateway(self)
        return straat
        

    def list_huisnummers_by_straat(self, straat, sort=1):
        '''
        List all `huisnummers` in a `straat`
        param object straat: An object of :class: `Straat`
        :rtype: A :class: `list` of :class: `Huisnummer`
        '''
        
        def creator():
            res=crab_gateway_request(self.client, 'ListHuisnummersWithStatusByStraatnaamId', straat, sort)
            return [
                Huisnummer(
                    r.HuisnummerId,
                    r.StatusHuisnummer,
                    r.Huisnummer,
                    gateway=self
                ) for r in res.HuisnummerWithStatusItem
            ]
            
        if self.caches['long'].is_configured:
            key='ListHuisnummersWithStatusByStraatnaamId#%s%s' %(straat, sort)
            return self.caches['long'].get_or_create(key, creator)
        else:
            return creator()


    def get_huisnummer_by_id(self,id):
        '''
        Retrieve a `huisnummer` by the Id.
        param integer id: the Id of the `huisnummer`
        :rtype :class: `Huisnummer`
        '''
        def creator():
            res=crab_gateway_request(self.client, 'GetHuisnummerWithStatusByHuisnummerId', id)
            return Huisnummer(
                res.HuisnummerId,
                res.StatusHuisnummer,
                res.Huisnummer,
                res.StraatnaamId
            )
        if self.caches['long'].is_configured:
            key='GetHuisnummerWithStatusByHuisnummerId#%s'%(id)
            huisnummer=self.caches['long'].get_or_create(key, creator)
        else: 
            huisnummer=creator()
        huisnummer.set_gateway(self)
        return huisnummer


    def get_huisnummer_by_nummer_and_straat(self, nummer, straat):
        '''
        Retrieve a `huisnummer` by the `nummer` and `straat`
        :rtype A :class: 'Huisnummer'
        '''
        def creator():
            res=crab_gateway_request(self.client, 'GetHuisnummerWithStatusByHuisnummer',nummer, straat)
            return Huisnummer(
                res.HuisnummerId,
                res.StatusHuisnummer,
                res.Huisnummer,
                res.StraatnaamId
            )
        if self.caches['long'].is_configured:
            key='GetHuisnummerWithStatusByHuisnummer#%s%s'%(nummer, straat)
            huisnummer=self.caches['long'].get_or_create(key, creator)
        else:
            huisnummer=creator()
        huisnummer.set_gateway(self)
        return huisnummer
    
    def list_postkantons_by_gemeente(self, gemeente):
        
        def creator():
            res=crab_gateway_request(self.client, 'ListPostkantonsByGemeenteId', gemeente)
            return[
                Postkanton(
                    r.PostkantonCode,
                    gateway=self
                )for r in res.PostkantonItem
            ] 
        if self.caches['long'].is_configured:
            key='ListPostkantonsByGemeenteId#%s'%(gemeente)
            return self.caches['long'].get_or_create(key, creator)
        else:
            return creator()


    def get_postkanton_by_huisnummer(self, huisnummer):
        
        def creator():
            res=crab_gateway_request(self.client, 'GetPostkantonByHuisnummerId', huisnummer)
            return Postkanton(
                res.PostkantonCode
            )
        if self.caches['long'].is_configured:
            key='GetPostkantonByHuisnummerId#%s'%(huisnummer)
            postkanton=self.caches['long'].get_or_create(key, creator)
        else:
            postkanton=creator()
        postkanton.set_gateway(self)
        return postkanton

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



class Gewest(GatewayObject):
    '''
    The smallest administrative unit in Belgium.
    '''
    
    def __init__(
        self,id,naam=None,
        **kwargs
    ):
       self.id=id
       self._naam=naam
       super(Gewest,self).__init__(**kwargs)
    
    @property
    def naam(self):
        return self._naam
        
    def __str__(self):
        if self.naam is not None:
            return "%s (%s)" %(self._naam, self.id)
        else:
            return "Gewest %s" % (self.id)
            
    def __repr__(self):
        if self.naam is not None:
            return"Gewest(%s, '%s')" % (self.id, self._naam)
        else:
            return "Gewest(%s)" %(self.id)


def check_lazy_load_gemeente(f):
    '''
    Decorator function to lazy load a :class: `Gemeente`.
    '''
    def wrapper(*args):
        gemeente=args[0]
        if gemeente._naam is None or gemeente._centroid is None or gemeente._bounding_box is None or gemeente._niscode is None or gemeente._gewest is None or gemeente._taal is None:
            gemeente.check_gateway()
            g=gemeente.gateway.get_gemeente_by_id(gemeente.id)
            gemeente._naam=g._naam
            gemeente._niscode=g._niscode
            gemeente._gewest=g._gewest
            gemeente._taal=g._taal
            gemeente._centroid=g._centroid
            gemeente._bounding_box=g._bounding_box
        return f(*args)
    return wrapper


class Gemeente(GatewayObject):
    '''
    The smallest administrative unit in Belgium.
    '''
    
    def __init__(
            self, id, naam=None, niscode=None, gewest=None, taal=None,
            centroid=None, bounding_box=None,
            **kwargs
    ):
        self.id=int(id)
        self._naam=naam
        self._niscode=niscode
        self._gewest=gewest
        self._taal=taal
        self._centroid=centroid
        self._bounding_box=bounding_box
        super(Gemeente,self).__init__(**kwargs)
    
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
        return self._gewest
        
    @property
    @check_lazy_load_gemeente
    def taal(self):
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
    def straten(self):
        self.check_gateway()
        return self.gateway.list_straten(self.id)
        
        
    @property
    def postkantons(self):
        self.check_gateway()
        return self.gateway.list_postkantons_by_gemeente(self.id)
    
    def __str__(self):
        if self._naam is not None:
            return "%s (%s)" %(self._naam,self.id)
        else:
            return "Gemeente %s" %(self.id)
            
    def __repr__(self):
        if self._naam is not None:
            return "Gemeente(%s, '%s')" %(self.id, self._naam)
        else:
            return "Gemeente(%s)" %(self.id)



class Codelijst(GatewayObject):
    def __init__(
            self, id, naam, definitie=None, **kwargs
    ):
        self.id=id
        self._naam=naam
        self._definitie=definitie
        super(Codelijst, self).__init__(**kwargs)
           
    @property
    def naam(self):
        return self._naam
        
    @property
    def definitie(self):
        return self._definitie

class Taal(Codelijst):
    pass
 
class Bewerking(Codelijst):
    pass
    
class Organisatie(Codelijst):
    pass
    
class Aardsubadres(Codelijst):
    pass
    
class Aardadres(Codelijst):
    pass 

class Aardgebouw(Codelijst):
    pass
    
class Aardwegobject(Codelijst):
    pass
    
class Aardterreinobject(Codelijst):
    pass
    
class Statushuisnummer(Codelijst):
    pass
    
class Statussubadres(Codelijst):
    pass
    
class Statusstraatnaam(Codelijst):
    pass
    
class Statuswegsegment(Codelijst):
    pass
    
class Geometriemethodewegsegment(Codelijst):
    pass 
    
class Statusgebouw(Codelijst):
    pass 
    
class Geometriemethodegebouw(Codelijst):
    pass 
    
class Herkomstadrespositie(Codelijst):
    pass 


def check_lazy_load_straat(f):
    '''
    Decorator function to lazy load a :class: `Straat`.
    '''
    def wrapper(*args):
        straat=args[0]
        if straat._label is None or straat._namen is None or straat._status_id is None or straat._gemeente_id is None:
            straat.check_gateway()
            s=straat.gateway.get_straat_by_id(straat.id)
            straat._label=s._label
            straat._gemeente_id=s._gemeente_id
            straat._namen=s._namen
            straat._status_id=s._status_id
        return f(*args)
    return wrapper

class Straat(GatewayObject):
    '''
    '''
    def __init__(
            self,id, label=None, status_id=None, straatnaam=None,taalcode=None,
            straatnaam2=None, taalcode2=None,
            gemeente_id=None,  **kwargs
    ):
        
        self.id=id
        self._label=label
        self._status_id=status_id
        self._namen=((straatnaam, taalcode), (straatnaam2,taalcode2))
        self._gemeente_id=gemeente_id
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
        res=self.gateway.get_gemeente_by_id(self._gemeente_id)
        return res
            
    @property
    @check_lazy_load_straat
    def status(self):
        res= self.gateway.list_statusstraatnamen()
        for r in res:
            if int(r.id)==int(self._status_id):
                return r
            
        
    @property
    def huisnummers(self):
        self.check_gateway()
        return self.gateway.list_huisnummers_by_straat(self.id)
        
    @property
    @check_lazy_load_straat
    def taal_id(self):
        return self.gemeente.taal
        
          
    def __str__(self):
        if self._label is not None:
            return "%s (%s)" %(self._label,self.id)
        else:
            return "Straat %s" %(self.id)
            
    def __repr__(self):
        if self._label is not None:
            return "Straat(%s, '%s')" %(self.id, self._label)
        else:
            return "Straat(%s)" %(self.id)
        
def check_lazy_load_huisnummer(f):
    '''
    Decorator function to lazy load a :class: `Huisnummer`.
    '''
    
    def wrapper(*args):
        huisnummer=args[0]
        if huisnummer._straat_id is None or huisnummer._huisnummer is None or huisnummer._status_id is None:
            huisnummer.check_gateway()
            h=huisnummer.gateway.get_huisnummer_by_id(huisnummer.id)
            huisnummer._straat_id=h._straat_id
            huisnummer._huisnummer=h._huisnummer
            huisnummer._status_id=h._status_id
        return f(*args)
    return wrapper

class Huisnummer(GatewayObject):
    
    def __init__(
            self, id, status_id=None, huisnummer=None,
            straat_id=None, **kwargs
    ):
        self.id=int(id)
        self._status_id=status_id
        self._huisnummer=huisnummer
        self._straat_id=straat_id
        super(Huisnummer, self).__init__(**kwargs)
    
    @property
    @check_lazy_load_huisnummer
    def straat(self):
        res=self.gateway.get_straat_by_id(self._straat_id)
        return res
        
    @property
    @check_lazy_load_huisnummer
    def huisnummer(self):
        return self._huisnummer
        
    @property
    @check_lazy_load_huisnummer
    def status(self):
        res= self.gateway.list_statushuisnummers()
        for r in res:
            if int(r.id) == int(self._status_id):
                return r
       
    @property
    def postkanton(self):
        self.check_gateway()
        return self.gateway.get_postkanton_by_huisnummer(self.id)
        
        
class Postkanton(GatewayObject):
    
    def __init__(self, id, **kwargs):
        self.id=int(id)
        super(Postkanton, self).__init__(**kwargs)
    

        
