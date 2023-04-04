"""
This script demonstrates using the crab gateway to get a single
`huisnummer` by id.
"""

from crabpy.client import crab_factory
from crabpy.gateway.crab import CrabGateway

g = CrabGateway(crab_factory())

huisnummer = g.get_huisnummer_by_id(4254655)

print(f"{huisnummer.id}: {huisnummer.postadres}")
