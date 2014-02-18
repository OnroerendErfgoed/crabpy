# -*- coding: utf-8 -*-
'''
'''

from crabpy.client import crab_factory, crab_request

from crabpy.gateway.crab import CrabGateway

crab = crab_factory()

g = CrabGateway(crab)

gemeente = g.get_gemeente_by_id(1)

print str(gemeente)
for s in gemeente.straten:
    print "* %s" % s
    for h in s.huisnummers:
        print "** %s" %h
