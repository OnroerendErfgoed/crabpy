# -*- coding: utf-8 -*-

class CrabGateway(object):
    '''
    A gateway to the CRAB webservice.
    '''

    def __init__(self, client, **kwargs):
        self.client = client

    def list_gewesten(self, sort=1):
        pass

    def list_gemeenten(self, gewest=2, sort=1):
        '''
        List all `gemeenten` in a `gewest`.

        :param integer gewest: What gewest to list the `gemeenten` for.
        :param integer sort: What field to sort on.
        :rtype: A :class:`list` of :class:`Gemeente`.
        '''
        pass

    def get_gemeente_by_id(self, id):
        '''
        Retrieve a `gemeente` by the crab id.

        :param integer id: The CRAB id of the gemeente.
        :rtype: :class:`Gemeente`
        '''
        pass

    def get_gemeente_by_niscode(self, niscode):
        '''
        Retrieve a `gemeente` by the NIScode.

        :param integer id: The NIScode of the gemeente.
        :rtype: :class:`Gemeente`
        '''
        pass


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
    pass

class Gemeente(GatewayObject):
    '''
    The smallest administrative unit in Belgium.
    '''
    pass
