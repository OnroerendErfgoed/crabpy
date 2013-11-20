from crabpy.client import capakey_factory, capakey_request

capakey = capakey_factory(
    user = 'USER',
    password = 'PASSWORD'
)

from crabpy.gateway.capakey import CapakeyGateway

g = CapakeyGateway(capakey)

gent = g.get_gemeente_by_id(44021)

print 'Afdelingen in Gent'
print '------------------'

print [str(a) for a in g.list_kadastrale_afdelingen_by_gemeente(gent)]

print 'Secties in GENT AFD 1'
print '---------------------'

print [str(s) for s in g.list_secties_by_afdeling(44021)]

print 'Percelen in GENT AFD 1, Sectie A'
print '--------------------------------'

print [str(p) for p in g.list_percelen_by_sectie(s)]

print 'Perceel 44021A3675/00A000'
print '-------------------------'

p = g.get_perceel_by_capakey('44021A3675/00A000')

print 'perceel: %s' % p.id
print 'capakey: %s' % p.capakey
print 'percid: %s' % p.percid
print 'grondnummer: %s' % p.grondnummer
print 'bisnummer: %s' % p.bisnummer
print 'exponent: %s' % p.exponent
print 'macht: %s' % p.macht
print 'sectie: %s' % p.sectie
print 'afdeling: %s'% p.sectie.afdeling
