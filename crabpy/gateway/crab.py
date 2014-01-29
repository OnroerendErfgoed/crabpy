# -*- coding: utf-8 -*-

class CrabGateway(object):
    '''
    A gateway to the CRAB webservice.
    '''

    def __init__(self, client, **kwargs):
        self.client = client

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
                    r.GewestNaam
                )for r in res.GewestItem
            ]

        if self.caches['long'].is_configured:
            key='ListGewesten#%s' %sort
            gewest=self.caches['long'].get_or_create(key,creator)
        else:
            gewest=creator()
            gewest.set_gateway(self)
        return gewest

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
                    r.NISGemeenteCode
                )for r in res.GemeenteItem
            ]
        if self.caches['long'].is_configured:
            key='ListGemeentenByGewestId#%s%s'%(gewest, sort)
            gemeente=self.caches['long'].get_or_create(key, creator)
        else:
            gemeente=creator()
        gemeente.set_gateway(self)
        return gemeente

    def get_gemeente_by_id(self, id):
        '''
        Retrieve a `gemeente` by the crab id.

        :param integer id: The CRAB id of the gemeente.
        :rtype: :class:`Gemeente`
        '''
        
        def creator():
            res=crab_gateway_request(self.client, 'GetGemeenteByGemeenteId', id)
            return Gemeente(
                res.NISGemeenteCode,
                res.GemeenteNaam,
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
                (res.CenterX, res.CenterY),
                (res.MinimumX, res.MinumumY, res.MaximumX, res.MaximumY)
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
                getattr('crabpy.gateway.crab',returnclass)(
                    r.Code,
                    r.Naam,
                    r.Definitie
                ) for r in res.CodeItem
            ]
        if self.caches['long'].is_configured:
            key=function+'#%s'%(sort)
            codeobject=self.caches['long'].get_or_create(key, creator)
        else:
            codeobject=creator()
        codeobject.set_gateway(self)
        return codeobject
        
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
        return self._list_codeobject('ListAardSubadressn',sort,'Aardsubadres')
        
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
        return self._list_codeobject('ListStatusStraatnamen ',sort,'Statusstraatnaam')
        
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
            res=crab_gateway_request(self.client, 'ListStraatnamenWithStatusByGemeente', gemeente, sort)
            return[ 
                Straat(
                    r.StraatnaamId,
                    r.straatnaamLabel,
                    r.StatusStraatnaam
                )for r in res.StraatnaamWithStatusItem
            ]
        if self.caches['long'].is_configured:
            key='ListStraatnamenWithStatusByGemeente#%s%s'%(gemeente, sort)
            straat=self.caches['long'].get_or_create(key, creator)
        else:
            straat=creator()
        straat.set_gateway(self)
        return straat
        
    def get_straat_by_id(self,id):
        '''
        Retrieve a `straat`by the Id.
         
        :param integer id: The id of the `straat`.
        :rtype: :class:`Straat`
        '''
        def creator():
            res=crab_gateway_request(self.client, 'GetStraatnaamWIthStatusByStraatnaamId', id)
            return Straat(
                    res.StraatnaamLabel,
                    res.StatusStraatnaam
            )

        if self.caches['long'].is_configured:
            key='GetStraatnaamWIthStatusByStraatnaamId#%s'%(id)
            straat=self.caches['long'].get_or_create(key, creator)
        else:
            straat=creator()
        straat.set_gateway(self)
        return straat
        

    def list_huisnummers_by_straat(self, straat, sort):
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
                    r.Huisnummer,
                    r.StatusHuisnummer
                ) for r in res.HuisnummerWithStatusItem
            ]
            
        if self.caches['long'].is_configured:
            key='ListHuisnummersWithStatusByStraatnaamId#%s%s' %(straat, sort)
            huisnummer=self.caches['long'].get_or_create(key, creator)
        else:
            huisnummer=creator()
        huisnummer.set_gateway(self)
        return huisnummer


    def get_huisnummer_by_id(self,id):
        '''
        Retrieve a `huisnummer` by the Id.
        param integer id: the Id of the `huisnummer`
        :rtype :class: `Huisnummer`
        '''
        def creator():
            res=crab_gateway_request(self.client, 'GetHuisnummerWithStatusByHuisnummerId', id)
            return(
                res.StraatnaamId,
                res.Huinummer,
                res.StatusHuisnummer
            )
        if self.caches['long'].is_configured:
            key='GetHuisnummerWithStatusByHuisnummerId#%s'%(id)
            huisnummer=self.caches['long'].get_or_create(key, creator)
        else: 
            huisnummer=creator()
        huisnummer.set_gateway()
        return huisnummer


    def get_huisnummer_by_nummer_and_straat(self, nummer, straat):
        '''
        Retrieve a `huisnummer` by the `nummer` and `straat`
        :rtype A :class: 'Huisnummer'
        '''
        def creator():
            res=crab_gateway_request(self.client, 'GetHuisnummerWithStatusByHuisnummer',nummer, straat)
            return(
                res.HuisnummerId,
                res.StatusHuisnummer
            )
        if self.caches['long'].is_configured:
            key='getHuisnummerWithStatusByHuisnummer#%s%s'%(nummer, straat)
            huisnummer=self.caches['long'].get_or_create(key, creator)
        else:
            huisnummer=creator()
        huisnummer.set_gateway()
        return huisnummer
    

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
       self.naam=naam
       super(Gewest,self).__init__(**kwargs)
    
        
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
        if gemeente._naam is None or gemeente._centroid is None or gemeente._bounding_box is None or gemeente._niscode is None or gemeente._gewest is None:
            gemeente.check_gateway()
            g=gemeente.gateway.get_gemeente_by_id(gemeente.id)
            gemeente._naam=g._naam
            gemeente._niscode=g._niscode
            gemeente._gewest=g._gewest
            gemeente._centroid=g._centroid
            gemeente._bounding_box=g._bounding_box
        return f(*args)
    return wrapper


class Gemeente(GatewayObject):
    '''
    The smallest administrative unit in Belgium.
    '''
    
    def __init__(
            self, id, naam=None, niscode=None, gewest=None,
            centroid=None, bounding_box=None,
            **kwargs
    ):
        self.id=int(id)
        self._naam=naam
        self._niscode=int(niscode)
        self._gewest=int(gewest)
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
    def centroid(self):
        return self._centroid
        
    @property
    @check_lazy_load_gemeente
    def bounding_box(self):
        return self._bounding_box
        
    @property
    def straten(self):
        self.check_gateway()
        return self.gateway.list_straten(self)
        
    
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


def check_lazy_load_codelijst(f):
    '''
    Decorator function to lazy load a :class: `Codelijst`.
    '''
    def wrapper(*args):
        codelijst=args[0]
        if codelijst._naam is None or codelijst._definitie is None:
            codelijst.check_gateway()
            c=codelijst.gateway.get_codelijst()
            codelijst._naam=c._naam
            codelijst._definitie=c._definitie
        return f(*args)
    return wrapper


class Codelijst(GatewayObject):
    def __init__(
            self, code, naam=None , definitie=None, **kwargs
    ):
        self._code=code
        self._naam=naam
        self._definitie=definitie
        super(Codelijst, self).__init__(**kwargs)
           
    @property
    @check_lazy_load_codelijst
    def naam(self):
        return self._naam
        
    @property
    @check_lazy_load_codelijst
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
    
class Statustraatnaam(Codelijst):
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
        if straat._label is None or straat._namen is None or straat._taal_code is None or straat._status is None:
            straat.check_gateway()
            s=straat.gateway.get_straat_by_id(straat.id)
            straat._label=s._label
            straat._namen=s._namen
            straat._taal_code=s._taal_code
            straat._status=s._status
        return f(*args)
    return wrapper

class Straat(GatewayObject):
    '''
    '''
    def __init__(
            self,id, label=None, namen=None,
            taal_code=None, status=None, **kwargs
    ):
        
        self.id=int(id)
        self._label=label
        self._namen=namen
        self._taal_code=taal_code
        self._status=status
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
    def taal_code(self):
        return self._taal_code
            
    @property
    @check_lazy_load_straat
    def status(self):
        return self._status
        
    @property
    def huisnummers(self):
        self.check_gateway()
        return self.gateway.list_huisnummers_by_straat(self)
          
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
        if self._straat is None or self._huisnummer is None or self._status is None:
            huisnummer.check_gateway()
            h=huisnummer.gateway.get_huisnummer_by_id(huisnummer.id)
            huisnummer._straat=h._straat
            huisnummer._huisnummer=h._huisnummer
            huisnummer._status=h._status
        return f(*args)
    return wrapper

class Huisnummer(GatewayObject):
    
    def __init__(
            self, id, straat=None, huisnummer=None,
            status=None, **kwargs
    ):
        self.id=int(id)
        self._straat=straat
        self._huisnummer=huisnummer
        self._status=status
        super(Huisnummer, self).__init__(**kwargs)
    
    @property
    @check_lazy_load_huisnummer
    def straat(self):
        return self._straat
        
    @property
    @check_lazy_load_huisnummer
    def huisnummer(self):
        return self._huisnummer
        
    @property
    @check_lazy_load_huisnummer
    def status(self):
        return self._status
        
    

        
