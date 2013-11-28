# -*- coding: utf-8 -*-
'''
This module contains utiltiy functions for interacting with AGIV soap services.

.. versionadded:: 0.1.0
'''

from suds.client import Client

from suds.wsse import Security
from crabpy.wsse import UsernameDigestToken
from datetime import datetime

from crabpy.wsa import Action, MessageID, To


def crab_factory(**kwargs):
    '''
    Factory that generates a CRAB client.

    :rtype: :class:`suds.client.Client`
    '''
    if 'wsdl' in kwargs:
        wsdl = kwargs['wsdl']
        del kwargs['wsdl']
    else:
        wsdl = "http://crab.agiv.be/wscrab/wscrab.svc?wsdl"
    c = Client(
        wsdl,
        **kwargs
    )
    return c


def capakey_factory(**kwargs):
    '''
    Factory that generates a CAPAKEY client.

    :rtype: :class:`suds.client.Client`
    '''
    if 'wsdl' in kwargs:
        wsdl = kwargs['wsdl']
        del kwargs['wsdl']
    else:
        wsdl = "http://ws.agiv.be/capakeyws/nodataset.asmx?WSDL"
    if 'user' in kwargs and 'password' in kwargs:
        user = kwargs['user']
        password = kwargs['password']
        del kwargs['user']
        del kwargs['password']
    else:
        raise ValueError(
            "You must specify a 'user' and a 'password'."
        )
    c = Client(
        wsdl,
        **kwargs
    )
    c.capakey_user = user
    c.capakey_password = password
    return c


def capakey_request(client, action, *args):
    '''
    Utility function help making requests to the CAPAKEY service.

    :param client: A :class:`suds.client.Client` for the CAPAKEY service.
    :param string action: Which method to call, eg. `ListAdmGemeenten`.
    :returns: Result of the SOAP call.
    '''
    security = Security()
    token = UsernameDigestToken(client.capakey_user, client.capakey_password)
    security.tokens.append(token)
    client.set_options(wsse=security)

    cm = getattr(client.service, action)
    a = Action(cm.method.soap.action)
    mid = MessageID()
    t = To('http://ws.agiv.be/capakeyws/nodataset.asmx')
    client.set_options(soapheaders=[a.xml(), t.xml(), mid.xml()])

    return getattr(client.service, action)(*args)
