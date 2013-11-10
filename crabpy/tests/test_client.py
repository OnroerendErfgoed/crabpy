# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

from crabpy.client import (
    crab_factory
)

def run_crab_integration_tests():
    from testconfig import config
    try:
        return config['crab']['run_integration_tests']
    except KeyError:
        return False

class CrabClientTests(unittest.TestCase):

    def setUp(self):
        self.crab = crab_factory()

    def tearDown(self):
        self.crab = None

    @unittest.skipUnless(run_crab_integration_tests(), 'No CRAB Integration tests required')
    def test_list_gemeenten(self):
        res = self.crab.service.ListGemeentenByGewestId(2)
