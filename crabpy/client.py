from suds.client import Client

from suds.wsse import Security
from suds_passworddigest.token import UsernameDigestToken
from datetime import datetime

from crabpy.wsa import Action, MessageID, To


def crab_factory(**kwargs):
    if 'wsdl' in kwargs:
        wsdl = kwargs['wsdl']
        del kwargs['wsdl']
    else:
        wsdl = "http://crab.agiv.be/wscrab/wscrab.svc?wsdl"
    if 'proxy' in kwargs:
        proxy = kwargs['proxy']
        del kwargs['proxy']
    c = Client(
        wsdl,
        **kwargs
    )
    return c


def capakey_factory(**kwargs):
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
    if 'proxy' in kwargs:
        proxy = kwargs['proxy']
        del kwargs['proxy']
    c = Client(
        wsdl,
        **kwargs
    )
    c.capakey_user = user
    c.capakey_password = password
    return c


def capakey_request(client, action, *args):
    security = Security()
    token = UsernameDigestToken(client.capakey_user, client.capakey_password)
    # Service can't handle microseconds.
    utc = datetime.utcnow()
    utc = datetime(utc.year, utc.month, utc.day, utc.hour, utc.minute, utc.second, tzinfo=utc.tzinfo)
    token.setcreated(utc)
    security.tokens.append(token)
    client.set_options(wsse=security)

    cm = getattr(client.service, action)
    a = Action(cm.method.soap.action)
    mid = MessageID()
    t = To('http://ws.agiv.be/capakeyws/nodataset.asmx')
    client.set_options(soapheaders=[a.xml(), t.xml(), mid.xml()])

    return getattr(client.service, action)(*args)
