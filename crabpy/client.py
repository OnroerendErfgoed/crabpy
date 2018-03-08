# -*- coding: utf-8 -*-
'''
This module contains utility functions for interacting with AGIV SOAP services.

.. versionadded:: 0.1.0
'''

from __future__ import unicode_literals

import logging
log = logging.getLogger(__name__)

from suds.client import Client


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
