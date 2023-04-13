"""
This script demonstrates using the crab gateway to walk the entire
address tree (street and number) of a `gemeente`.
"""

from crabpy.client import crab_factory
from crabpy.gateway.crab import CrabGateway

g = CrabGateway(crab_factory())

gemeente = g.get_gemeente_by_id(1)

print(str(gemeente))
for s in gemeente.straten:
    print("* %s" % s)
    for h in s.huisnummers:
        print("\t* %s" % h)
        for sa in h.subadressen:
            print("\t\t* %s" % sa)
