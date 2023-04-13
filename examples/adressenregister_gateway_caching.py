"""
This script demonstrates querying the adressen register gateway while
maintaining a cache.

In total this script should execute 3 rest calls:
Retrieve gemeenten, retrieve straten, retrieve adressen.
"""
from crabpy.client import AdressenRegisterClient
from crabpy.gateway.adressenregister import Gateway

cache_settings = {
    "long.backend": "dogpile.cache.redis",
    "long.backend.replace_existing_backend": True,
    "short.backend": "dogpile.cache.redis",
    "short.backend.replace_existing_backend": True,
}
gateway = Gateway(
    AdressenRegisterClient("https://api.basisregisters.vlaanderen.be", None),
    cache_settings=cache_settings,
)
antwerpen = gateway.get_provincie_by_id("10000")
aartselaar = antwerpen.gemeenten[0]

print("Straten in AARTSELAAR (1)")
print("-------------------------")
print([str(straat) for straat in gateway.list_straten(aartselaar)])
print("Straten in AARTSELAAR (2)")
print("-------------------------")
print([str(straat) for straat in aartselaar.straten])

straat = aartselaar.straten[1]
print("Adressen in AARTSELAAR Straat1 (1)")
print("----------------------------------")
print([str(huisnummer) for huisnummer in gateway.list_adressen_by_straat(straat)])
print("Adressen in AARTSELAAR Straat1 (2)")
print("----------------------------------")
print([str(huisnummer) for huisnummer in straat.adressen])
