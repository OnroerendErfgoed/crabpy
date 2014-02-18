# -*- coding: utf-8 -*-
'''
This script demonstrates using the crab gateway to walk the entire
address tree (street and number) of a `gemeente`.
'''

from crabpy.client import crab_factory

from crabpy.gateway.crab import CrabGateway

crab = crab_factory()

g = CrabGateway(crab)

gemeente = g.get_gemeente_by_id(1)

print str(gemeente)
for s in gemeente.straten:
    print "* %s" % s
    for h in s.huisnummers:
        print "** %s" % h
