# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

from crabpy.client import (
    capakey_factory
)

from crabpy.gateway.crab import (
    CrabGateway,
    Gewest,
    Gemeente
)


def run_crab_integration_tests():
    from testconfig import config
    from crabpy.tests import as_bool
    try:
        return as_bool(config['crab']['run_integration_tests'])
    except KeyError:  # pragma NO COVER
        return False


@unittest.skipUnless(
    run_crab_integration_tests(),
    'No CRAB Integration tests required'
)
class CrabGatewayTests(unittest.TestCase):

    def setUp(self):
        from testconfig import config
        self.crab_client = crab_factory()
        self.crab = CrabGateway(
            self.crab_client
        )

    def tearDown(self):
        self.crab_client = None
        self.crab = None
     
	def test_list_gewesten(self):
		res=self.crab.list_gewesten()
		self.assertIsInstance(res, list)
		
	def test_list_gemeenten(self):
		res=self.crab.list_gemeenten()
		self.assertIsInstance(res, list)
		
	def test_get_gemeente_by_id(self):
		res=self.crab.get_gemeente_by_id(272)
		self.assertIsInstance(res, Gemeente)
		self.assertIsEqual(res.id, 272)
		
	def test_get_gemeente_by_invalid_id(self):
		pass
		
	def test_get_gemeente_by_niscode(self):
		res=self.crab.get_gemeente_by_niscode(11001)
		self.assertIsInstance(res, Gemeente)
		self.assertsEqual(res.niscode, 11001)
	


class GemeenteTests(unittest.TestCase):
	
    def setUp(self):
		from testconfig import config
		self.crab_client = crab_factory()
		self.crab = CrabGateway(
		    self.crab_client
        )

    def tearDown(self):
        self.crab_client = None
        self.crab = None
	
	def test_fully_initialised(self):
		 g = Gemeente(
            1,
            'Aartselaar',
            11001,
            2,
            (150881.07, 202146.08),
            (148950.36, 199938.28, 152811.77, 204575.39)
        )
        self.assertEqual(g.id, 1)
        self.assertEqual(g.naam, 'Aartselaar')
        self.assertEqual(g.niscode, 11001)
        self.assertEqual(g.gewest, 2)
        self.assertEqual(g.centroid, (150881.07, 202146.08))
        self.assertEqual(
            g.bounding_box,
            (148950.36, 199938.28, 152811.77, 204575.39)
        )
        self.assertEqual('Aartselaar (11001)', str(g))
        self.assertEqual("Gemeente(11001, 'Aartselaar')", repr(g))
        
	
class GewestenTests(unittest.TestCase):
	
    def setUp(self):
		from testconfig import config
		self.crab_client = crab_factory()
		self.crab = CrabGateway(
		    self.crab_client
        )

    def tearDown(self):
        self.crab_client = None
        self.crab = None
	
	def test_fully_initialised(self):
		 g = Gewest(
            2,
           ' '','
        )
        self.assertEqual(g.id, 2)
        'self.assertEqual(g.naam, '')'
        
