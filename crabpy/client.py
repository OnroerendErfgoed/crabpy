# -*- coding: utf-8 -*-
'''
This module contains utility functions for interacting with AGIV SOAP services.

.. versionadded:: 0.1.0
'''

from __future__ import unicode_literals

import logging
log = logging.getLogger(__name__)

from suds.client import Client

from suds.wsse import Security
from crabpy.wsse import UsernameDigestToken

from crabpy.wsa import Action, MessageID, To


def crab_factory(**kwargs):
    '''
    Factory that generates a CRAB client.

    A few parameters will be handled by the factory, other parameters will
    be passed on to the client.

    :param wsdl: `Optional.` Allows overriding the default CRAB wsdl url.
    :param proxy: `Optional.` A dictionary of proxy information that is passed
        to the underlying :class:`suds.client.Client`
    :rtype: :class:`suds.client.Client`
    '''
    if 'wsdl' in kwargs:
        wsdl = kwargs['wsdl']
        del kwargs['wsdl']
    else:
        wsdl = "http://crab.agiv.be/wscrab/wscrab.svc?wsdl"
    log.info('Creating CRAB client with wsdl: %s', wsdl)
    c = Client(
        wsdl,
        **kwargs
    )
    return c


def capakey_factory(**kwargs):
    '''
    Factory that generates a CAPAKEY client.

    A few parameters will be handled by the factory, other parameters will
    be passed on to the client.

    :param user: `Required.` Username for authenticating with the CAPAKEY
        service.
    :param password: `Required.` Password for authenticating with the CAPAKEY
        service.
    :param wsdl: `Optional.` Allows overriding the default CAPAKEY wsdl url.
    :param proxy: `Optional.` A dictionary of proxy information that is passed
        to the underlying :class:`suds.client.Client`
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
    log.info('Creating CAPAKEY client with wsdl: %s', wsdl)
    c = Client(
        wsdl,
        **kwargs
    )
    c.capakey_user = user
    c.capakey_password = password
    return c


def crab_request(client, action, *args):
    '''
    Utility function that helps making requests to the CRAB service.

    :param client: A :class:`suds.client.Client` for the CRAB service.
    :param string action: Which method to call, eg. `ListGewesten`
    :returns: Result of the SOAP call.

    .. versionadded:: 0.3.0
    '''
    log.debug('Calling %s on CRAB service.', action)
    return getattr(client.service, action)(*args)


def capakey_request(client, action, *args):
    '''
    Utility function that helps making requests to the CAPAKEY service.

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

    log.debug('Calling %s on CAPAKEY service.', action)
    return getattr(client.service, action)(*args)
