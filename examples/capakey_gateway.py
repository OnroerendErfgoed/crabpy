# -*- coding: utf-8 -*-
"""
This script demonstrates using the capakey gateway to walk the entire
cadastral tree of a `gemeente`.

WARNING: The CapakeyGateway (SOAP) is deprecated, use CapakeyRestGateway (REST) instead.
"""

from crabpy.client import capakey_factory

capakey = capakey_factory(
    user = 'USER',
    password = 'PASSWORD'
)

from crabpy.gateway.capakey import CapakeyGateway

g = CapakeyGateway(capakey)

gemeente = g.get_gemeente_by_id(45062)

print(str(gemeente))
for a in gemeente.afdelingen:
    print("* %s" % a)
    for s in a.secties:
        print("\t* %s" % s)
        for p in s.percelen:
            print("\t\t* %s" % p)
