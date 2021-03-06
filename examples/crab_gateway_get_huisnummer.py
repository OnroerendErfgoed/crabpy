# -*- coding: utf-8 -*-
'''
This script demonstrates using the crab gateway to get a single
`huisnummer` by id.
'''

from crabpy.client import crab_request, crab_factory
from crabpy.gateway.crab import CrabGateway

g = CrabGateway(crab_factory())

huisnummer = g.get_huisnummer_by_id(4254655)

print("%s: %s" % (huisnummer.id, huisnummer.postadres))
