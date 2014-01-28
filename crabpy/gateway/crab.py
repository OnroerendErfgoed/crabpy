# -*- coding: utf-8 -*-

class CrabGateway(object):
    '''
    A gateway to the CRAB webservice.
    '''

    def __init__(self, client, **kwargs):
        self.client = client

    def list_gewesten(self, sort=1):
        pass
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
        pass
        
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
		if self.name is not None:
			return "%s (%s)" %(self._naam, self.id)
		else:
			return "Gewest %s " % (self.id)
			
    def __repr__(self):
		if self._naam is not None:
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
			self, id, naam,niscode=None,gewest=None,
			centroid=None, bounding_box=None,
			**kwargs
	):
		self._id=int(id)
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
		
	
    def __str__(self):
		if self.name is not None:
			return "%s (%s)" %(self._naam,self.id)
		else:
			return "Gemeente %s" %(self.id)
			
    def __repr__(self):
		if self._naam is not None:
			return "Gemeente(%s, '%s')" %(self.id, self._naam)
		else:
			return "Gewest(%s)" %(self.id)
