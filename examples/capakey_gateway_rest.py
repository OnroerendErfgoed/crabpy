"""
This script demonstrates using the capakey rest gateway to walk the entire
cadastral tree of a `gemeente`.

"""

from crabpy.gateway.capakey import CapakeyRestGateway

g = CapakeyRestGateway()

gemeente = g.get_gemeente_by_id(45062)

print(str(gemeente))
for a in gemeente.afdelingen:
    print("* %s" % a)
    for s in a.secties:
        print("\t* %s" % s)
        for p in s.percelen:
            print("\t\t* %s" % p)
