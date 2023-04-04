"""
This script demonstrates querying the crab gateway while maintaining a cache.
"""

import os

from crabpy.client import crab_factory

from crabpy.gateway.crab import CrabGateway

root = "./dogpile_data/"

if not os.path.exists(root):
    os.makedirs(root)

g = CrabGateway(
    crab_factory(),
    cache_config={
        "permanent.backend": "dogpile.cache.dbm",
        "permanent.expiration_time": 604800,
        "permanent.arguments.filename": os.path.join(root, "crab_permanent.dbm"),
        "long.backend": "dogpile.cache.dbm",
        "long.expiration_time": 86400,
        "long.arguments.filename": os.path.join(root, "crab_long.dbm"),
    },
)


aartselaar = g.get_gemeente_by_id(1)

print("Straten in AARTSELAAR")
print("---------------------")
print([str(s) for s in g.list_straten(aartselaar)])

print("Huisnummers in AARTSELAAR Straat1")
print("---------------------------------")
# print([str(h) for h in g.list_huisnummers_by_straat(s)])

p = g.get_gemeente_by_niscode(33021)

print("gemeente: %s" % p.id)
print("naam: %s" % p.naam)
print("niscode: %s" % p.niscode)
print("gewest: %s" % p.gewest)
print("provincie: %s" % p.provincie)
print("taal: %s" % p.taal)
print("centroid: %s" % str(p.centroid))
print("bounding_box: %s" % str(p.bounding_box))
