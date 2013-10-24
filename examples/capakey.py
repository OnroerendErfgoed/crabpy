from crabpy.client import capakey_factory, capakey_request

capakey = capakey_factory(
    user='USER',
    password='PASSWORD'
)

res = capakey_request(capakey, 'ListAdmGemeenten', 1)

print res
