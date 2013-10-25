from crabpy.client import capakey_factory, capakey_request

capakey = capakey_factory(
    user='USER',
    password='PASSWORD'
)

print capakey

res = capakey_request(capakey, 'ListAdmGemeenten', 1)

print res

res = capakey_request(capakey, 'ListKadAfdelingenByNiscode', 44021, 1)

print res

print capakey_request(capakey, 'ListKadSectiesByKadAfdelingcode', 44021)

print capakey_request(capakey, 'ListKadPerceelsnummersByKadSectiecode', 44021, 'A', 1)

print capakey_request(capakey, 'GetKadPerceelsnummerByCaPaKey', '44021A3675/00A000')
