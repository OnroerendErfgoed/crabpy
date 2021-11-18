"""
This script prints all available information on the CRAB webservice.
"""

from crabpy.client import crab_factory

crab = crab_factory()

print(crab)
