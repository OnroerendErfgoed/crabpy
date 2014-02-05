# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

from crabpy.client import (
    crab_factory
)

from crabpy.gateway.crab import (
    CrabGateway, Gewest,
    Gemeente, Taal,
    Bewerking, Organisatie,
    Aardsubadres, Aardadres,
    Aardgebouw, Aardwegobject,
    Aardterreinobject, Statushuisnummer,
    Statussubadres, Statusstraatnaam,
    Statuswegsegment, Geometriemethodewegsegment,
    Statusgebouw, Geometriemethodegebouw,
    Herkomstadrespositie,Straat,
    Huisnummer, Postkanton
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
        res=self.crab.get_gemeente_by_id(1)
        self.assertIsInstance(res, Gemeente)
        self.assertEqual(res.id, 1)
        
    '''def test_get_gemeente_by_invalid_id(self):
        from crabpy.gateway.exception import GatewayRuntimeException
        res=self.crab.get_gemeente_by_id('gent')
        self.assertRaises(WebFault)'''
            
        
    def test_get_gemeente_by_niscode(self):
        res=self.crab.get_gemeente_by_niscode(11001)
        self.assertIsInstance(res, Gemeente)
        self.assertEqual(res.niscode, 11001)
    
    def test_list_talen(self):
        res=self.crab.list_talen()
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
        res=self.crab.list_statussubadressen()
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
    
    def test_get_straat_by_id(self):
        res=self.crab.get_straat_by_id(1)
        self.assertIsInstance(res, Straat)
        self.assertEqual(res.id, 1)
        
    def test_list_huisnummers_by_straat(self):
        res=self.crab.list_huisnummers_by_straat(1)
        self.assertIsInstance(res, list)
        
    def test_get_huisnummer_by_id(self):
        res=self.crab.get_huisnummer_by_id(1)
        self.assertIsInstance(res, Huisnummer)
        self.assertEqual(res.id, 1)
        
    def test_get_huisnummer_by_nummer_and_straat(self):
        res=self.crab.get_huisnummer_by_nummer_and_straat(1,1)
        self.assertIsInstance(res, Huisnummer)
        self.assertEqual(res.huisnummer, '1')
        self.assertEqual(res.straat, 1)
        
    def test_list_postkantons_by_gemeente(self):
        res=self.crab.list_postkantons_by_gemeente(1)
        self.assertIsInstance(res, list)
        
    def test_get_postkanton_by_huisnummer(self):
        res=self.crab.get_postkanton_by_huisnummer(1)
        self.assertIsInstance(res, Postkanton)

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
            g=Gemeente(1)
            self.assertEqual('Gemeente 1', str(g))
            self.assertEqual('Gemeente(1)', repr(g))
            
        def test_check_gateway_not_set(self):
            g=Gemeente(1)
            self.assertRaises(RuntimeError, g.check_gateway)
            

class GewestTests(unittest.TestCase):
    

    def test_fully_initialised(self):
        g = Gewest(
            2,
        )
        self.assertEqual(g.id,2)
        '''Nog verder uitbreiden met naam'''
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
        '''Nog verder uitbreiden als ik de juiste gegevens heb'''
    def test_check_gateway_not_set(self):
        t=Taal(1)
        self.assertRaises(RuntimeError, t.check_gateway)
        
class BewerkingTests(unittest.TestCase):
    def test_fully_initialised(self):
        pass
        '''Nog verder uitbreiden als ik de juiste gegevens heb'''
    def test_check_gateway_not_set(self):
        b=Bewerking(1)
        self.assertRaises(RuntimeError, b.check_gateway)
        
class OrganisatieTests(unittest.TestCase):
    def test_fully_initialised(self):
        pass
        '''Nog verder uitbreiden als ik de juiste gegevens heb'''
    def test_check_gateway_not_set(self):
        o=Organisatie(1)
        self.assertRaises(RuntimeError, o.check_gateway)
        
class AardsubadresTests(unittest.TestCase):
    def test_fully_initialised(self):
        pass
        '''Nog verder uitbreiden als ik de juiste gegevens heb'''
    def test_check_gateway_not_set(self):
        a=Aardsubadres(1)
        self.assertRaises(RuntimeError, a.check_gateway)
        
class AardadresTests(unittest.TestCase):
    def test_fully_initialised(self):
        pass
        '''Nog verder uitbreiden als ik de juiste gegevens heb'''
    def test_check_gateway_not_set(self):
        a=Aardadres(1)
        self.assertRaises(RuntimeError, a.check_gateway)
        
class AardgebouwTests(unittest.TestCase):
    def test_fully_initialised(self):
        pass
        '''Nog verder uitbreiden als ik de juiste gegevens heb'''
    def test_check_gateway_not_set(self):
        a=Aardgebouw(1)
        self.assertRaises(RuntimeError, a.check_gateway)

class AardwegobjectTests(unittest.TestCase):
    def test_fully_initialised(self):
        pass
        '''Nog verder uitbreiden als ik de juiste gegevens heb'''
    
    def test_check_gateway_not_set(self):
        a=Aardwegobject(1)
        self.assertRaises(RuntimeError,a.check_gateway)
        
    def test_str_and_repr_dont_lazy_load(self):
        s=Straat(1)
        self.assertEqual('Straat 1', str(s))
        self.assertEqual('Straat(1)', repr(s))

class HuisnummerTests(unittest.TestCase):
    def test_fully_initialised(self):
        h=Huisnummer(1)
        self.assertEqual(h.id, 1)
        '''Nog verder uitbreiden als ik de juiste gegevens heb'''
    def test_check_gateway_not_set(self):
        h=Huisnummer(1)
        self.assertRaises(RuntimeError, h.check_gateway)
        
class PostkantonTests(unittest.TestCase):
    def test_fully_initialised(self):
        p = Postkanton( 1)
        self.assertEqual(p.id, 1)
        
    
@unittest.skipUnless(run_crab_integration_tests(), 'No CRAB Integration tests required')
class CrabCachedGatewayTests(unittest.TestCase):

    def setUp(self):
        self.crab_client=crab_factory()
        self.crab = CrabGateway(
            self.crab_client,
            cache_config = {
                'permanent.backend': 'dogpile.cache.memory',
                'permanent.expiration_time': 86400,
                'long.backend': 'dogpile.cache.memory',
                'long.expiration_time': 3600,
                'short.backend': 'dogpile.cache.memory',
                'short.expiration_time': 600,
            }
        )

    def tearDown(self):
        self.crab_client = None
        self.crab = None

    def test_cache_is_configured(self):
        from dogpile.cache.backends.memory import MemoryBackend
        self.assertIsInstance(
            self.crab.caches['permanent'].backend, 
            MemoryBackend
        )
        self.assertTrue(self.crab.caches['permanent'].is_configured)
        
    
    def test_list_gewesten(self):
        res = self.crab.list_gewesten()
        self.assertIsInstance(res, list)
        self.assertEqual(
            self.crab.caches['permanent'].get('ListGewesten#1'),
            res
        )

    def test_list_gewesten_different_sort(self):
        res = self.crab.list_gewesten(2)
        self.assertIsInstance(res, list)
        self.assertEqual(
            self.crab.caches['permanent'].get('ListGewesten#2'),
            res
        )
        from dogpile.cache.api import NO_VALUE
        self.assertEqual(
            self.crab.caches['permanent'].get('ListGewesten#1'),
            NO_VALUE
        )

    def test_list_gemeenten(self):
        res = self.crab.list_gemeenten()
        self.assertIsInstance(res, list)
        self.assertEqual(
            self.crab.caches['long'].get('ListGemeentenByGewestId#21'),
            res
        )

    def test_list_gemeenten_different_sort_and_gewest(self):
        res = self.crab.list_gemeenten(1,2)
        self.assertIsInstance(res, list)
        self.assertEqual(
            self.crab.caches['long'].get('ListGemeentenByGewestId#12'),
            res
        )
        from dogpile.cache.api import NO_VALUE
        self.assertEqual(
            self.crab.caches['long'].get('ListGemeentenByGewestId#21'),
            NO_VALUE
        )
        

        

