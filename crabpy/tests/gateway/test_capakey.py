# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

from crabpy.client import (
    capakey_factory
)

from crabpy.gateway.capakey import (
    CapakeyGateway,
    Gemeente,
    Afdeling,
    Sectie,
    Perceel
)


def run_capakey_integration_tests():
    from testconfig import config
    from crabpy.tests import as_bool
    try:
        return as_bool(config['capakey']['run_integration_tests'])
    except KeyError:  # pragma NO COVER
        return False


@unittest.skipUnless(
    run_capakey_integration_tests(),
    'No CAPAKEY Integration tests required'
)
class CapakeyGatewayTests(unittest.TestCase):

    def setUp(self):
        from testconfig import config
        self.capakey_client = capakey_factory(
            user=config['capakey']['user'],
            password=config['capakey']['password']
        )
        self.capakey = CapakeyGateway(
            self.capakey_client
        )

    def tearDown(self):
        self.capakey_client = None
        self.capakey = None

    def test_list_gemeenten(self):
        res = self.capakey.list_gemeenten()
        self.assertIsInstance(res, list)

    def test_list_gemeenten_invalid_auth(self):
        self.capakey_client = capakey_factory(
            user='USER',
            password='PASSWORD'
        )
        self.capakey = CapakeyGateway(
            self.capakey_client
        )
        from crabpy.gateway.exception import GatewayAuthenticationException
        with self.assertRaises(GatewayAuthenticationException):
            self.capakey.list_gemeenten()

    def test_get_gemeente_by_id(self):
        res = self.capakey.get_gemeente_by_id(44021)
        self.assertIsInstance(res, Gemeente)
        self.assertEqual(res.id, 44021)

    def test_get_gemeente_by_invalid_id(self):
        from crabpy.gateway.exception import GatewayRuntimeException
        with self.assertRaises(GatewayRuntimeException):
            self.capakey.get_gemeente_by_id('gent')

    def test_list_afdelingen(self):
        res = self.capakey.list_kadastrale_afdelingen()
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 300)

    def test_list_afdelingen_by_gemeente(self):
        g = self.capakey.get_gemeente_by_id(44021)
        res = self.capakey.list_kadastrale_afdelingen_by_gemeente(g)
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 0)
        self.assertLess(len(res), 40)

    def test_list_afdelingen_by_gemeente_id(self):
        res = self.capakey.list_kadastrale_afdelingen_by_gemeente(44021)
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 0)
        self.assertLess(len(res), 40)

    def test_get_kadastrale_afdeling_by_id(self):
        res = self.capakey.get_kadastrale_afdeling_by_id(44021)
        self.assertIsInstance(res, Afdeling)
        self.assertEqual(res.id, 44021)
        self.assertIsInstance(res.gemeente, Gemeente)
        self.assertEqual(res.gemeente.id, 44021)

    def test_list_secties_by_afdeling(self):
        a = self.capakey.get_kadastrale_afdeling_by_id(44021)
        res = self.capakey.list_secties_by_afdeling(a)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)

    def test_list_secties_by_afdeling_id(self):
        res = self.capakey.list_secties_by_afdeling(44021)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)

    def test_get_sectie_by_id_and_afdeling(self):
        a = self.capakey.get_kadastrale_afdeling_by_id(44021)
        res = self.capakey.get_sectie_by_id_and_afdeling('A', a)
        self.assertIsInstance(res, Sectie)
        self.assertEqual(res.id, 'A')
        self.assertEqual(res.afdeling.id, 44021)

    def test_list_percelen_by_sectie(self):
        s = self.capakey.get_sectie_by_id_and_afdeling('A', 44021)
        res = self.capakey.list_percelen_by_sectie(s)
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 0)

    def test_get_perceel_by_id_and_sectie(self):
        s = self.capakey.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = self.capakey.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = self.capakey.get_perceel_by_id_and_sectie(perc.id, s)
        self.assertIsInstance(res, Perceel)
        self.assertEqual(res.sectie.id, 'A')
        self.assertEqual(res.sectie.afdeling.id, 44021)

    def test_get_perceel_by_capakey(self):
        s = self.capakey.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = self.capakey.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = self.capakey.get_perceel_by_capakey(perc.capakey)
        self.assertIsInstance(res, Perceel)
        self.assertEqual(res.sectie.id, 'A')
        self.assertEqual(res.sectie.afdeling.id, 44021)

    def test_get_perceel_by_percid(self):
        s = self.capakey.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = self.capakey.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = self.capakey.get_perceel_by_percid(perc.percid)
        self.assertIsInstance(res, Perceel)
        self.assertEqual(res.sectie.id, 'A')
        self.assertEqual(res.sectie.afdeling.id, 44021)


class GemeenteTests(unittest.TestCase):

    def test_fully_initialised(self):
        g = Gemeente(
            44021,
            'Gent',
            (104154.2225, 197300.703),
            (94653.453, 185680.984, 113654.992, 208920.422)
        )
        self.assertEqual(g.id, 44021)
        self.assertEqual(g.naam, 'Gent')
        self.assertEqual(g.centroid, (104154.2225, 197300.703))
        self.assertEqual(
            g.bounding_box,
            (94653.453, 185680.984, 113654.992, 208920.422)
        )
        self.assertEqual('Gent (44021)', str(g))
        self.assertEqual("Gemeente(44021, 'Gent')", repr(g))

    def test_str_and_repr_dont_lazy_load(self):
        g = Gemeente(44021)
        self.assertEqual('Gemeente 44021', str(g))
        self.assertEqual('Gemeente(44021)', repr(g))

    def test_check_gateway_not_set(self):
        g = Gemeente(44021)
        self.assertRaises(RuntimeError, g.check_gateway)

    @unittest.skipUnless(
        run_capakey_integration_tests(),
        'No CAPAKEY Integration tests required'
    )
    def test_lazy_load(self):
        from testconfig import config
        capakey = CapakeyGateway(
            capakey_factory(
                user=config['capakey']['user'],
                password=config['capakey']['password']
            )
        )
        g = Gemeente(44021)
        g.set_gateway(capakey)
        self.assertEqual(g.id, 44021)
        self.assertEqual(g.naam, 'Gent')
        self.assertIsNotNone(g.centroid)
        self.assertIsNotNone(g.bounding_box)

    @unittest.skipUnless(
        run_capakey_integration_tests(),
        'No CAPAKEY Integration tests required'
    )
    def test_afdelingen(self):
        from testconfig import config
        capakey = CapakeyGateway(
            capakey_factory(
                user=config['capakey']['user'],
                password=config['capakey']['password']
            )
        )
        g = Gemeente(44021)
        g.set_gateway(capakey)
        afdelingen = g.afdelingen
        self.assertIsInstance(afdelingen, list)
        self.assertGreater(len(afdelingen), 0)
        self.assertLess(len(afdelingen), 40)


class AfdelingTests(unittest.TestCase):

    def test_fully_initialised(self):
        a = Afdeling(
            44021,
            'GENT  1 AFD',
            Gemeente(44021, 'Gent'),
            (104893.06375, 196022.244094),
            (104002.076625, 194168.3415, 105784.050875, 197876.146688)
        )
        self.assertEqual(a.id, 44021)
        self.assertEqual(a.naam, 'GENT  1 AFD')
        self.assertEqual(a.centroid, (104893.06375, 196022.244094))
        self.assertEqual(
            a.bounding_box,
            (104002.076625, 194168.3415, 105784.050875, 197876.146688)
        )
        self.assertEqual('GENT  1 AFD (44021)', str(a))
        self.assertEqual("Afdeling(44021, 'GENT  1 AFD')", repr(a))

    def test_to_string_not_fully_initialised(self):
        a = Afdeling(
            44021
        )
        self.assertEqual('Afdeling 44021', str(a))

    def test_check_gateway_not_set(self):
        a = Afdeling(44021)
        self.assertRaises(RuntimeError, a.check_gateway)

    @unittest.skipUnless(
        run_capakey_integration_tests(),
        'No CAPAKEY Integration tests required'
    )
    def test_lazy_load(self):
        from testconfig import config
        capakey = CapakeyGateway(
            capakey_factory(
                user=config['capakey']['user'],
                password=config['capakey']['password']
            )
        )
        a = Afdeling(44021)
        a.set_gateway(capakey)
        self.assertEqual(a.id, 44021)
        self.assertEqual(a.naam, 'GENT  1 AFD')
        self.assertIsNotNone(a.centroid)
        self.assertIsNotNone(a.bounding_box)

    @unittest.skipUnless(
        run_capakey_integration_tests(),
        'No CAPAKEY Integration tests required'
    )
    def test_secties(self):
        from testconfig import config
        capakey = CapakeyGateway(
            capakey_factory(
                user=config['capakey']['user'],
                password=config['capakey']['password']
            )
        )
        a = Afdeling(44021)
        a.set_gateway(capakey)
        secties = a.secties
        self.assertIsInstance(secties, list)
        self.assertEqual(len(secties), 1)


class SectieTests(unittest.TestCase):

    def test_fully_initialised(self):
        s = Sectie(
            'A',
            Afdeling(44021, 'Gent  1 AFD'),
            (104893.06375, 196022.244094),
            (104002.076625, 194168.3415, 105784.050875, 197876.146688)
        )
        self.assertEqual(s.id, 'A')
        self.assertEqual(s.centroid, (104893.06375, 196022.244094))
        self.assertEqual(
            s.bounding_box,
            (104002.076625, 194168.3415, 105784.050875, 197876.146688)
        )
        self.assertEqual('Gent  1 AFD (44021), Sectie A', str(s))
        self.assertEqual(
            "Sectie('A', Afdeling(44021, 'Gent  1 AFD'))",
            repr(s)
        )

    def test_check_gateway_not_set(self):
        s = Sectie('A', Afdeling(44021))
        self.assertRaises(RuntimeError, s.check_gateway)

    @unittest.skipUnless(
        run_capakey_integration_tests(),
        'No CAPAKEY Integration tests required'
    )
    def test_lazy_load(self):
        from testconfig import config
        capakey = CapakeyGateway(
            capakey_factory(
                user=config['capakey']['user'],
                password=config['capakey']['password']
            )
        )
        s = Sectie(
            'A',
            Afdeling(44021)
        )
        s.set_gateway(capakey)
        self.assertEqual(s.id, 'A')
        self.assertEqual(s.afdeling.id, 44021)
        self.assertIsNotNone(s.centroid)
        self.assertIsNotNone(s.bounding_box)

    @unittest.skipUnless(
        run_capakey_integration_tests(),
        'No CAPAKEY Integration tests required'
    )
    def test_percelen(self):
        from testconfig import config
        capakey = CapakeyGateway(
            capakey_factory(
                user=config['capakey']['user'],
                password=config['capakey']['password']
            )
        )
        s = Sectie(
            'A',
            Afdeling(44021)
        )
        s.set_gateway(capakey)
        percelen = s.percelen
        self.assertIsInstance(percelen, list)
        self.assertGreater(len(percelen), 0)


class PerceelTests(unittest.TestCase):

    def test_fully_initialised(self):
        p = Perceel(
            '1154/02C000', Sectie('A', Afdeling(46013)),
            '40613A1154/02C000', '40613_A_1154_C_000_02',
            'capaty', 'cashkey',
            (104893.06375, 196022.244094),
            (104002.076625, 194168.3415, 105784.050875, 197876.146688)
        )
        self.assertEqual(p.id, ('1154/02C000'))
        self.assertEqual(p.sectie.id, 'A')
        self.assertEqual(p.capatype, 'capaty')
        self.assertEqual(p.cashkey, 'cashkey')
        self.assertEqual(
            p.centroid,
            (104893.06375, 196022.244094)
        )
        self.assertEqual(
            p.bounding_box,
            (104002.076625, 194168.3415, 105784.050875, 197876.146688)
        )
        self.assertEqual(p.capakey, str(p))
        self.assertEqual(
            "Perceel('1154/02C000', Sectie('A', Afdeling(46013)), '40613A1154/02C000', '40613_A_1154_C_000_02')",
            repr(p)
        )

    def test_check_gateway_not_set(self):
        p = Perceel(
            '1154/02C000', Sectie('A', Afdeling(46013)),
            '40613A1154/02C000', '40613_A_1154_C_000_02'
        )
        self.assertRaises(RuntimeError, p.check_gateway)

    @unittest.skipUnless(
        run_capakey_integration_tests(),
        'No CAPAKEY Integration tests required'
    )
    def test_lazy_load(self):
        from testconfig import config
        capakey = CapakeyGateway(
            capakey_factory(
                user=config['capakey']['user'],
                password=config['capakey']['password']
            )
        )
        p = Perceel(
            '1154/02C000', Sectie('A', Afdeling(46013)),
            '46013A1154/02C000', '46013_A_1154_C_000_02',
            gateway=capakey
        )
        self.assertEqual(p.id, '1154/02C000')
        self.assertEqual(p.sectie.id, 'A')
        self.assertEqual(p.sectie.afdeling.id, 46013)
        self.assertIsNotNone(p.capatype)
        self.assertIsNotNone(p.cashkey)
        self.assertIsNotNone(p.centroid)
        self.assertIsNotNone(p.bounding_box)

    def test_parse_capakey(self):
        p = Perceel(
            '1154/02C000', Sectie('A', Afdeling(46013)),
            '46013A1154/02C000', '46013_A_1154_C_000_02'
        )
        self.assertEqual(p.grondnummer, '1154')
        self.assertEqual(p.bisnummer, '02')
        self.assertEqual(p.exponent, 'C')
        self.assertEqual(p.macht, '000')

    def test_parse_capakey_other_sectie(self):
        p = Perceel(
            '1154/02C000', Sectie('F', Afdeling(46013)),
            '46013F1154/02C000', '46013_F_1154_C_000_02'
        )
        self.assertEqual(p.grondnummer, '1154')
        self.assertEqual(p.bisnummer, '02')
        self.assertEqual(p.exponent, 'C')
        self.assertEqual(p.macht, '000')

    def test_parse_invalid_capakey(self):
        with self.assertRaises(ValueError):
            Perceel(
                '1154/02C000', Sectie('A', Afdeling(46013)),
                '46013_A_1154_C_000_02',
                '46013A1154/02C000',
            )


@unittest.skipUnless(
    run_capakey_integration_tests(),
    'No CAPAKEY Integration tests required'
)
class CapakeyCachedGatewayTests(unittest.TestCase):

    def setUp(self):
        from testconfig import config
        self.capakey_client = capakey_factory(
            user=config['capakey']['user'],
            password=config['capakey']['password']
        )
        self.capakey = CapakeyGateway(
            self.capakey_client,
            cache_config={
                'permanent.backend': 'dogpile.cache.memory',
                'permanent.expiration_time': 86400,
                'long.backend': 'dogpile.cache.memory',
                'long.expiration_time': 3600,
                'short.backend': 'dogpile.cache.memory',
                'short.expiration_time': 600,
            }
        )

    def tearDown(self):
        self.capakey_client = None
        self.capakey = None

    def test_cache_is_configured(self):
        from dogpile.cache.backends.memory import MemoryBackend
        self.assertIsInstance(
            self.capakey.caches['permanent'].backend,
            MemoryBackend
        )
        self.assertTrue(self.capakey.caches['permanent'].is_configured)

    def test_list_gemeenten(self):
        res = self.capakey.list_gemeenten()
        self.assertIsInstance(res, list)
        self.assertEqual(
            self.capakey.caches['permanent'].get('ListAdmGemeenten#1'),
            res
        )

    def test_list_gemeenten_different_sort(self):
        res = self.capakey.list_gemeenten(2)
        self.assertIsInstance(res, list)
        self.assertEqual(
            self.capakey.caches['permanent'].get('ListAdmGemeenten#2'),
            res
        )
        from dogpile.cache.api import NO_VALUE
        self.assertEqual(
            self.capakey.caches['permanent'].get('ListAdmGemeenten#1'),
            NO_VALUE
        )

    def test_get_gemeente_by_id(self):
        res = self.capakey.get_gemeente_by_id(44021)
        self.assertIsInstance(res, Gemeente)
        self.assertEqual(
            self.capakey.caches['long'].get('GetAdmGemeenteByNiscode#44021'),
            res
        )

    def test_list_afdelingen(self):
        res = self.capakey.list_kadastrale_afdelingen()
        self.assertIsInstance(res, list)
        self.assertEqual(
            self.capakey.caches['permanent'].get('ListKadAfdelingen#1'),
            res
        )

    def test_list_afdelingen_by_gemeente(self):
        g = self.capakey.get_gemeente_by_id(44021)
        self.assertEqual(
            self.capakey.caches['long'].get('GetAdmGemeenteByNiscode#44021'),
            g
        )
        res = self.capakey.list_kadastrale_afdelingen_by_gemeente(g)
        self.assertIsInstance(res, list)
        self.assertEqual(
            self.capakey
                .caches['permanent']
                .get('ListKadAfdelingenByNiscode#44021#1'),
            res
        )

    def test_get_kadastrale_afdeling_by_id(self):
        res = self.capakey.get_kadastrale_afdeling_by_id(44021)
        self.assertIsInstance(res, Afdeling)
        self.assertEqual(res.id, 44021)
        self.assertIsInstance(res.gemeente, Gemeente)
        self.assertEqual(res.gemeente.id, 44021)
        self.assertEqual(
            self.capakey
                .caches['long']
                .get('GetKadAfdelingByKadAfdelingcode#44021'),
            res
        )

    def test_list_secties_by_afdeling_id(self):
        res = self.capakey.list_secties_by_afdeling(44021)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertEqual(
            self.capakey
                .caches['long']
                .get('ListKadSectiesByKadAfdelingcode#44021'),
            res
        )

    def test_get_sectie_by_id_and_afdeling(self):
        a = self.capakey.get_kadastrale_afdeling_by_id(44021)
        res = self.capakey.get_sectie_by_id_and_afdeling('A', a)
        self.assertIsInstance(res, Sectie)
        self.assertEqual(res.id, 'A')
        self.assertEqual(res.afdeling.id, 44021)
        self.assertEqual(
            self.capakey
                .caches['long']
                .get('GetKadSectieByKadSectiecode#44021#A'),
            res
        )

    def test_list_percelen_by_sectie(self):
        s = self.capakey.get_sectie_by_id_and_afdeling('A', 44021)
        res = self.capakey.list_percelen_by_sectie(s)
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 0)
        self.assertEqual(
            self.capakey
                .caches['short']
                .get('ListKadPerceelsnummersByKadSectiecode#44021#A#1'),
            res
        )

    def test_get_perceel_by_id_and_sectie(self):
        s = self.capakey.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = self.capakey.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = self.capakey.get_perceel_by_id_and_sectie(perc.id, s)
        self.assertIsInstance(res, Perceel)
        self.assertEqual(res.sectie.id, 'A')
        self.assertEqual(res.sectie.afdeling.id, 44021)
        self.assertEqual(
            self.capakey
                .caches['short']
                .get('GetKadPerceelsnummerByKadPerceelsnummer#44021#A#%s' % perc.id),
            res
        )

    def test_get_perceel_by_capakey(self):
        s = self.capakey.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = self.capakey.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = self.capakey.get_perceel_by_capakey(perc.capakey)
        self.assertIsInstance(res, Perceel)
        self.assertEqual(res.sectie.id, 'A')
        self.assertEqual(res.sectie.afdeling.id, 44021)
        self.assertEqual(
            self.capakey
                .caches['short']
                .get('GetKadPerceelsnummerByCaPaKey#%s' % perc.capakey),
            res
        )

    def test_get_perceel_by_percid(self):
        s = self.capakey.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = self.capakey.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = self.capakey.get_perceel_by_percid(perc.percid)
        self.assertIsInstance(res, Perceel)
        self.assertEqual(res.sectie.id, 'A')
        self.assertEqual(res.sectie.afdeling.id, 44021)
        self.assertEqual(
            self.capakey
                .caches['short']
                .get('GetKadPerceelsnummerByPERCID#%s' % perc.percid),
            res
        )
