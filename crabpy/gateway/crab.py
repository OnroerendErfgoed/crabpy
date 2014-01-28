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
				)for r in res.'''GewestItem??'''
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
				)for r in res.'''Gemeente??'''
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
			return gemeente(
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
		centroid=None, bounding_box=None,
		**kwargs
   ):
	   self.id=id
	   self.naam=naam
	   self.centroid=centroid
	   self.bounding_box=bounding_box
	   super(Gewest,self).__init__(**kwargs)
	

class Gemeente(GatewayObject):
    '''
    The smallest administrative unit in Belgium.
    '''
    
     def __init__(
			self, id, naam=None,gewest=None
			centroid=None, bounding_box=None,
			**kwargs
	):
		self.id=int(id)
		self.naam=naam
		self.gewest=gewest
		self.centroid=centroid
		self.bounding_box=bounding_box
		super(Gemeente,self).__init__(**kwargs)
