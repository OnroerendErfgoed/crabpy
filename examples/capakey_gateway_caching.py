"""
This script demonstrates querying the capakey gateway while maintaining a cache.

WARNING: The CapakeyGateway (SOAP) is deprecated, use CapakeyRestGateway (REST) instead.
"""

import os

from crabpy.client import capakey_factory
from crabpy.gateway.capakey import CapakeyGateway

capakey = capakey_factory(user="USER", password="PASSWORD")

root = "./dogpile_data/"

if not os.path.exists(root):
    os.makedirs(root)

g = CapakeyGateway(
    capakey,
    cache_config={
        "permanent.backend": "dogpile.cache.dbm",
        "permanent.expiration_time": 604800,
        "permanent.arguments.filename": os.path.join(root, "capakey_permanent.dbm"),
        "long.backend": "dogpile.cache.dbm",
        "long.expiration_time": 86400,
        "long.arguments.filename": os.path.join(root, "capakey_long.dbm"),
        "short.backend": "dogpile.cache.dbm",
        "short.expiration_time": 3600,
        "short.arguments.filename": os.path.join(root, "capakey_short.dbm"),
    },
)

gent = g.get_gemeente_by_id(44021)

print("Afdelingen in Gent")
print("------------------")

print([str(a) for a in g.list_kadastrale_afdelingen_by_gemeente(gent)])

print("Secties in GENT AFD 1")
print("---------------------")

print([str(s) for s in g.list_secties_by_afdeling(44021)])

print("Percelen in GENT AFD 1, Sectie A")
print("--------------------------------")

s = g.get_sectie_by_id(44021, "A")
print([str(p) for p in g.list_percelen_by_sectie(s)])

print("Perceel 44021A3675/00A000")
print("-------------------------")

p = g.get_perceel_by_capakey("44021A3675/00A000")

print("perceel: %s" % p.id)
print("capakey: %s" % p.capakey)
print("percid: %s" % p.percid)
print("grondnummer: %s" % p.grondnummer)
print("bisnummer: %s" % p.bisnummer)
print("exponent: %s" % p.exponent)
print("macht: %s" % p.macht)
print("sectie: %s" % p.sectie)
print("afdeling: %s" % p.sectie.afdeling)
