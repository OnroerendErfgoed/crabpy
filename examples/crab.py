"""
This script demonstrates using the crab client directly or through the
:func:`crabpy.client.crab_request` function.
"""

from crabpy.client import crab_factory, crab_request

crab = crab_factory()

res = crab.service.ListGemeentenByGewestId(1)
print(res)

res = crab.service.ListPostkantonsByGemeenteId(71)
print(res)

res = crab_request(crab, "ListGemeentenByGewestId", 1)
print(res)

res = crab_request(crab, "ListHuisnummersWithStatusByStraatnaamId", 18618)
print(res)

res = crab_request(crab, "GetStraatnaamWithStatusByStraatnaamId", 18618)
print(res)
