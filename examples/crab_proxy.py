"""
This script show how to connect to the WS-WRAB service through a proxy.
"""

from crabpy.client import crab_factory

crab = crab_factory(
    proxy={
        "http": "http://proxy.example.com:3128",
        "https": "https://httpsproxy.example.com:3128",
    }
)

print(crab.service.ListGemeentenByGewestId(1))
