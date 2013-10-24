from crabpy.client import crab_factory

crab = crab_factory()

res = crab.service.ListGemeentenByGewestId(1)

print res
