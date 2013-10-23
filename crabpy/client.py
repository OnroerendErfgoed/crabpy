from suds.client import Client

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
        
