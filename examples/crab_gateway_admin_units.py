"""
This script demonstrates using the crab gateway to walk the entire
address tree (street and number) of a `gemeente`.
"""

from crabpy.client import crab_factory
from crabpy.gateway.crab import CrabGateway

g = CrabGateway(crab_factory())

gewesten = g.list_gewesten()

print("Administratieve eenheden in België")
print("----------------------------------")
for gw in gewesten:
    print("\n")
    print("\t%s" % str(gw))
    print("\t" + ("-" * len(str(gw))))
    for p in gw.provincies:
        print("\n")
        print("\t\t%s" % str(p))
        print("\t\t" + ("-" * len(str(p))))
        for g in p.gemeenten:
            print(f"\t\t\t* {g.naam} ({g.niscode})")
