from crabpy.client import crab_factory

crab = crab_factory()

'''res = crab.service.ListGemeentenByGewestId(1)
print res

res = crab.service.ListPostkantonsByGemeenteId(71)
print res

res = crab.service.ListStraatnamenWithStatusByGemeenteId(71)
print res 

res = crab.service.ListHuisnummersWithStatusByStraatnaamId(18618)
print res

res = crab.service.GetStraatnaamWithStatusByStraatnaamId(18618)
print res'''


res = crab.service.GetWegobjectByIdentificatorWegobject(53840456)

print res


