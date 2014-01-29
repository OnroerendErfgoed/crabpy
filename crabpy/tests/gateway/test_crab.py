# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

from crabpy.client import (
    crab_factory
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
    
    def test_list_talen(self):
        res=self.crab.list_talen(self)
        self.assertIsInstance(res, list)
        
    def test_list_bewerkingen(self):
        res=self.crab.list_bewerkingen()
        self.assertIsInstance(res,list)
    
    def test_list_organisaties(self):
        res=self.crab.list_organisaties()
        self.assertIsInstance(res, list)
        
    def test_list_aardsubadressen(self):
        res=self.crab.list_aardsubadressen()
        self.assertIsInstance(res, list)
        
    def test_list_aardadressen(self):
        res=self.crab.list_aardadressen()
        self.assertIsInstance(res, list)
        
    def test_list_aardgebouwen(self):
        res=self.crab.list_aardgebouwen()
        self.assertIsInstance(res, list)
        
    def test_list_aarwegobjecten(self):
        res=self.crab.list_aardwegobjecten()
        self.assertIsInstance(res, list)
        
    def test_list_aardterreinobjecten(self):
        res=self.crab.list_aardterreinobjecten()
        self.assertIsInstance(res, list)
        
    def test_list_statushuisnummers(self):
        res=self.crab.list_statushuisnummers()
        self.assertIsInstance(res, list)
        
    def test_list_statussubadressen(self):
        res=self.crab.list_statussubadressen
        self.assertIsInstance(res, list)
        
    def test_list_statusstraatnamen(self):
        res=self.crab.list_statusstraatnamen()
        self.assertIsInstance(res, list)
        
    def test_list_statuswegsegmenten(self):
        res=self.crab.list_statuswegsegmenten()
        self.assertIsInstance(res, list)
        
    def test_list_geometriemethodewegsegmenten(self):
        res=self.crab.list_geometriemethodewegsegmenten()
        self.assertIsInstance(res, list)
        
    def test_list_statusgebouwen(self):
        res=self.crab.list_statusgebouwen()
        self.assertIsInstance(res, list)
        
    def test_list_gemetriemethodegebouwen(self):
        res=self.crab.list_geometriemethodegebouwen()
        self.assertIsInstance(res, list)
        
    def test_list_herkomstadrespositie(self):
        res=self.crab.list_herkomstadresposities()
        self.assertIsInstance(res, list)
        
    def test_list_straten(self):
        res=self.crab.list_straten(1)
        self.assertIsInstance(res, list)
        self.assertIsEqual(res.GemeenteId, 1)
    
''' def test_get_straat_by_id(self):
        res=self.crab.get_straat_by_id()
        self.assertIsInstance(res, Straat)
        self.assertIsEqual(res.i, )'''
        
        

class GemeenteTests(unittest.TestCase):
    
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
        self.assertEqual('Aartselaar (1)', str(g))
        self.assertEqual("Gemeente(1, 'Aartselaar')", repr(g))
        
        
        def test_str_and_repr_dont_lazy_load(self):
            g=Gemeente(11001)
            self.assertEqual('Gemeente 1', str(g))
            self.assertEqual('Gemeente(1)', repr(g))
            
        def test_check_gateway_not_set(self):
            g=Gemeente(11001)
            self.assertRaises(RuntimeError, g.check_gateway)
            

class GewestTests(unittest.TestCase):
    

    def test_fully_initialised(self):
        g = Gewest(
            2,
        )
        self.assertEqual(g.id,2)
        
    def test_str_and_repr_dont_lazy_load(self):
        g=Gewest(2)
        self.assertEqual('Gewest 2', str(g))
        self.assertEqual('Gewest(2)', repr(g))
            
    def test_check_gateway_not_set(self):
        g=Gewest(2)
        self.assertRaises(RuntimeError, g.check_gateway)
        
class TaalTests(unittest.TestCase):
    def test_fully_initialised(self):
        pass
        
    def test_check_gateway_not_set(self):
        pass
        t=Taal()
        self.assertRaises(RuntimeError, t.check_gateway)
        
class BewerkingTests(unittest.TestCase):
    def test_fully_initialised(self):
        pass
        
    def test_check_gateway_not_set(self):
        pass
        b=Bewerking()
        self.assertRaises(RuntimeError, b.check_gateway)
        
class OrganisatieTests(unittest.TestCase):
    def test_fully_initialised(self):
        pass
        
    def test_check_gateway_not_set(self):
        pass
        o=Organisatie()
        self.assertRaises(RuntimeError, o.check_gateway)
        
class AardsubadresTests(unittest.TestCase):
    def test_fully_initialised(self):
        pass
        
    def test_check_gateway_not_set(self):
        pass
        a=Aardsubadres()
        self.assertRaises(RuntimeError, a.check_gateway)
        
class AardadresTests(unittest.TestCase):
    def test_fully_initialised(self):
        pass
        
    def test_check_gateway_not_set(self):
        pass
        a=Aardadres()
        self.assertRaises(RuntimeError, a.check_gateway)
        
class AardgebouwTests(unittest.TestCase):
    def test_fully_initialised(self):
        pass
        
    def test_check_gateway_not_set(self):
        pass
        a=Aardgebouw()
        self.assertRaises(RuntimeError, a.check_gateway)

class AardwegobjectTests(unittest.TestCase):
    def test_fully_initialised(self):
        pass
    
    def test_check_gateway_not_set(self):
        pass
        a=Aardwegobject()
        self.assertRaises(RuntimeError,a.check_gateway)
        
    def test_str_and_repr_dont_lazy_load(self):
        pass
        s=Straat()
        self.assertEqual('Straat 2', str(g))
        self.assertEqual('Straat(2)', repr(g))

    
    
    
