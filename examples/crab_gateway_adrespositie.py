"""
This script demonstrates using the crab gateway to get information about the
position of an `adres`.
"""

from crabpy.client import crab_factory
from crabpy.gateway.crab import CrabGateway

g = CrabGateway(crab_factory())

straat = g.get_straat_by_id(48086)

print(str(straat))
for h in straat.huisnummers:
    print("\t* %s" % h)
    for ap in h.adresposities:
        print(f"\t\t* {ap.herkomst}: {ap.geometrie}")
