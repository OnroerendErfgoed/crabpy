# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa
import pytest

from crabpy.client import (
    capakey_factory
)

from crabpy.gateway.exception import (
    GatewayResourceNotFoundException
)

from crabpy.gateway.capakey import (
    CapakeyGateway,
    Gemeente,
    Afdeling,
    Sectie,
    Perceel
)

from tests import (
    run_capakey_integration_tests,
    config
)

@pytest.mark.skipif(
    not pytest.config.getoption('--capakey-integration'),
    reason = 'No CAPAKEY Integration tests required'
)
class TestCapakeyGateway:

    def test_list_gemeenten(self, capakey_gateway):
        res = capakey_gateway.list_gemeenten()
        assert isinstance(res, list)

    def test_list_gemeenten_invalid_auth(self):
        capakey_gateway_client = capakey_factory(
            user='USER',
            password='PASSWORD'
        )
        capakey_gateway = CapakeyGateway(
            capakey_gateway_client
        )
        from crabpy.gateway.exception import GatewayAuthenticationException
        with pytest.raises(GatewayAuthenticationException):
            capakey_gateway.list_gemeenten()

    def test_get_gemeente_by_id(self, capakey_gateway):
        res = capakey_gateway.get_gemeente_by_id(44021)
        assert isinstance(res, Gemeente)
        assert res.id == 44021

    def test_get_gemeente_by_invalid_id(self, capakey_gateway):
        with pytest.raises(GatewayResourceNotFoundException):
            capakey_gateway.get_gemeente_by_id('gent')

    def test_list_afdelingen(self, capakey_gateway):
        res = capakey_gateway.list_kadastrale_afdelingen()
        assert isinstance(res, list)
        assert len(res) > 300

    def test_list_afdelingen_by_gemeente(self, capakey_gateway):
        g = capakey_gateway.get_gemeente_by_id(44021)
        res = capakey_gateway.list_kadastrale_afdelingen_by_gemeente(g)
        assert isinstance(res, list)
        assert len(res) > 0
        assert len(res) < 40

    def test_list_afdelingen_by_unexisting_gemeente(self, capakey_gateway):
        g = Gemeente(99999)
        res = capakey_gateway.list_kadastrale_afdelingen_by_gemeente(g)
        assert isinstance(res, list)
        assert len(res) == 0

    def test_list_afdelingen_by_gemeente_id(self, capakey_gateway):
        res = capakey_gateway.list_kadastrale_afdelingen_by_gemeente(44021)
        assert isinstance(res, list)
        assert len(res) > 0
        assert len(res) < 40

    def test_get_kadastrale_afdeling_by_id(self, capakey_gateway):
        res = capakey_gateway.get_kadastrale_afdeling_by_id(44021)
        assert isinstance(res, Afdeling)
        assert res.id == 44021
        assert isinstance(res.gemeente, Gemeente)
        assert res.gemeente.id == 44021

    def test_get_kadastrale_afdeling_by_unexisting_id(self, capakey_gateway):
        with pytest.raises(GatewayResourceNotFoundException):
            capakey_gateway.get_kadastrale_afdeling_by_id(44000)

    def test_list_secties_by_afdeling(self, capakey_gateway):
        a = capakey_gateway.get_kadastrale_afdeling_by_id(44021)
        res = capakey_gateway.list_secties_by_afdeling(a)
        assert isinstance(res, list)
        assert len(res) ==  1

    def test_list_secties_by_unexisting_afdeling(self, capakey_gateway):
        a = Afdeling(99000)
        res = capakey_gateway.list_secties_by_afdeling(a)
        assert isinstance(res, list)
        assert len(res) ==  0

    def test_list_secties_by_afdeling_id(self, capakey_gateway):
        res = capakey_gateway.list_secties_by_afdeling(44021)
        assert isinstance(res, list)
        assert len(res) == 1

    def test_get_sectie_by_id_and_afdeling(self, capakey_gateway):
        a = capakey_gateway.get_kadastrale_afdeling_by_id(44021)
        res = capakey_gateway.get_sectie_by_id_and_afdeling('A', a)
        assert isinstance(res, Sectie)
        assert res.id == 'A'
        assert res.afdeling.id == 44021

    def test_get_sectie_by_unexisting_id_and_afdeling(self, capakey_gateway):
        a = capakey_gateway.get_kadastrale_afdeling_by_id(44021)
        with pytest.raises(GatewayResourceNotFoundException):
            capakey_gateway.get_sectie_by_id_and_afdeling('Z', a)

    def test_list_percelen_by_sectie(self, capakey_gateway):
        s = capakey_gateway.get_sectie_by_id_and_afdeling('A', 44021)
        res = capakey_gateway.list_percelen_by_sectie(s)
        assert isinstance(res, list)
        assert len(res) > 0

    def test_list_percelen_by_unexisting_sectie(self, capakey_gateway):
        s = Sectie('Z', Afdeling(99000))
        res = capakey_gateway.list_percelen_by_sectie(s)
        assert isinstance(res, list)
        assert len(res) ==  0

    def test_get_perceel_by_id_and_sectie(self, capakey_gateway):
        s = capakey_gateway.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = capakey_gateway.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = capakey_gateway.get_perceel_by_id_and_sectie(perc.id, s)
        assert isinstance(res, Perceel)
        assert res.sectie.id == 'A'
        assert res.sectie.afdeling.id == 44021

    def test_get_perceel_by_unexisting_id_and_sectie(self, capakey_gateway):
        s = capakey_gateway.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = capakey_gateway.list_percelen_by_sectie(s)
        perc = percelen[0]
        with pytest.raises(GatewayResourceNotFoundException):
            capakey_gateway.get_perceel_by_id_and_sectie(-1, s)

    def test_get_perceel_by_capakey(self, capakey_gateway):
        s = capakey_gateway.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = capakey_gateway.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = capakey_gateway.get_perceel_by_capakey(perc.capakey)
        assert isinstance(res, Perceel)
        assert res.sectie.id == 'A'
        assert res.sectie.afdeling.id == 44021

    def test_get_perceel_by_unexisting_capakey(self, capakey_gateway):
        with pytest.raises(GatewayResourceNotFoundException):
            capakey_gateway.get_perceel_by_capakey('0000000')

    def test_get_perceel_by_percid(self, capakey_gateway):
        s = capakey_gateway.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = capakey_gateway.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = capakey_gateway.get_perceel_by_percid(perc.percid)
        assert isinstance(res, Perceel)
        assert res.sectie.id == 'A'
        assert res.sectie.afdeling.id == 44021

    def test_get_perceel_by_unexisting_percid(self, capakey_gateway):
        with pytest.raises(GatewayResourceNotFoundException):
            capakey_gateway.get_perceel_by_percid('0000/0000')


class TestGemeente:

    def test_fully_initialised(self):
        g = Gemeente(
            44021,
            'Gent',
            (104154.2225, 197300.703),
            (94653.453, 185680.984, 113654.992, 208920.422)
        )
        assert (g.id, 44021)
        assert (g.naam, 'Gent')
        assert (g.centroid, (104154.2225, 197300.703))
        assert (
            g.bounding_box,
            (94653.453, 185680.984, 113654.992, 208920.422)
        )
        assert ('Gent (44021)', str(g))
        assert ("Gemeente(44021, 'Gent')", repr(g))

    def test_str_and_repr_dont_lazy_load(self):
        g = Gemeente(44021, 'Gent')
        assert ('Gent (44021)', str(g))
        assert ("Gemeente(44021, 'Gent')", repr(g))

    def test_check_gateway_not_set(self):
        g = Gemeente(44021, 'Gent')
        with pytest.raises(RuntimeError):
            g.check_gateway()

    @pytest.mark.skipif(
        not pytest.config.getoption('--capakey-integration'),
        reason = 'No CAPAKEY Integration tests required'
    )
    def test_lazy_load(self, capakey_gateway):
        g = Gemeente(44021, 'Gent', gateway=capakey_gateway)
        g.clear_gateway()
        with pytest.raises(RuntimeError):
            g.check_gateway()

    @pytest.mark.skipif(
        not pytest.config.getoption('--capakey-integration'),
        reason = 'No CAPAKEY Integration tests required'
    )
    def test_lazy_load(self, capakey_gateway):
        g = Gemeente(44021, 'Gent')
        g.set_gateway(capakey_gateway)
        assert g.id == 44021
        assert g.naam == 'Gent'
        assert not g.centroid == None
        assert not g.bounding_box == None

    @pytest.mark.skipif(
        not pytest.config.getoption('--capakey-integration'),
        reason = 'No CAPAKEY Integration tests required'
    )
    def test_afdelingen(self, capakey_gateway):
        g = Gemeente(44021, 'Gent')
        g.set_gateway(capakey_gateway)
        afdelingen = g.afdelingen
        assert isinstance(afdelingen, list)
        assert len(afdelingen) > 0
        assert len(afdelingen) < 40


class TestAfdeling:

    def test_fully_initialised(self):
        a = Afdeling(
            44021,
            'GENT  1 AFD',
            Gemeente(44021, 'Gent'),
            (104893.06375, 196022.244094),
            (104002.076625, 194168.3415, 105784.050875, 197876.146688)
        )
        assert a.id == 44021
        assert a.naam == 'GENT  1 AFD'
        assert a.centroid == (104893.06375, 196022.244094)
        assert a.bounding_box == (104002.076625, 194168.3415, 105784.050875, 197876.146688)
        assert 'GENT  1 AFD (44021)' == str(a)
        assert "Afdeling(44021, 'GENT  1 AFD')" == repr(a)

    def test_partially_initialised(self):
        a = Afdeling(
            44021,
            'GENT  1 AFD',
            Gemeente(44021, 'Gent'),
        )
        assert a.id ==44021
        assert a.naam == 'GENT  1 AFD'
        assert 'GENT  1 AFD (44021)' == str(a)
        assert "Afdeling(44021, 'GENT  1 AFD')" == repr(a)

    def test_to_string_not_fully_initialised(self):
        a = Afdeling(
            44021
        )
        assert 'Afdeling 44021' == str(a)

    def test_check_gateway_not_set(self):
        a = Afdeling(44021)
        with pytest.raises(RuntimeError):
            a.check_gateway()

    @pytest.mark.skipif(
        not pytest.config.getoption('--capakey-integration'),
        reason = 'No CAPAKEY Integration tests required'
    )
    def test_lazy_load(self, capakey_gateway):
        a = Afdeling(44021)
        a.set_gateway(capakey_gateway)
        assert a.id == 44021
        assert a.naam == 'GENT  1 AFD'
        assert not a.centroid == None
        assert not a.bounding_box == None

    @pytest.mark.skipif(
        not pytest.config.getoption('--capakey-integration'),
        reason = 'No CAPAKEY Integration tests required'
    )
    def test_secties(self, capakey_gateway):
        a = Afdeling(44021)
        a.set_gateway(capakey_gateway)
        secties = a.secties
        assert isinstance(secties, list)
        assert len(secties) == 1


class TestSectie:

    def test_fully_initialised(self):
        s = Sectie(
            'A',
            Afdeling(44021, 'Gent  1 AFD'),
            (104893.06375, 196022.244094),
            (104002.076625, 194168.3415, 105784.050875, 197876.146688)
        )
        assert s.id == 'A'
        assert s.centroid == (104893.06375, 196022.244094)
        assert s.bounding_box == (104002.076625, 194168.3415, 105784.050875, 197876.146688)
        assert ('Gent  1 AFD (44021), Sectie A', str(s))
        assert "Sectie('A', Afdeling(44021, 'Gent  1 AFD'))" == repr(s)

    def test_check_gateway_not_set(self):
        s = Sectie('A', Afdeling(44021))
        with pytest.raises(RuntimeError):
            s.check_gateway()

    def test_clear_gateway(self, capakey_gateway):
        s = Sectie('A', Afdeling(44021))
        s.set_gateway(capakey_gateway)
        s.check_gateway()
        s.clear_gateway()
        with pytest.raises(RuntimeError):
            s.check_gateway()

    @pytest.mark.skipif(
        not pytest.config.getoption('--capakey-integration'),
        reason = 'No CAPAKEY Integration tests required'
    )
    def test_lazy_load(self, capakey_gateway):
        s = Sectie(
            'A',
            Afdeling(44021)
        )
        s.set_gateway(capakey_gateway)
        assert s.id == 'A'
        assert s.afdeling.id == 44021
        assert not s.centroid == None
        assert not s.bounding_box == None

    @pytest.mark.skipif(
        not pytest.config.getoption('--capakey-integration'),
        reason = 'No CAPAKEY Integration tests required'
    )
    def test_percelen(self, capakey_gateway):
        s = Sectie(
            'A',
            Afdeling(44021)
        )
        s.set_gateway(capakey_gateway)
        percelen = s.percelen
        assert isinstance(percelen, list)
        assert len(percelen) > 0


class TestPerceel:

    def test_fully_initialised(self):
        p = Perceel(
            '1154/02C000', Sectie('A', Afdeling(46013)),
            '40613A1154/02C000', '40613_A_1154_C_000_02',
            'capaty', 'cashkey',
            (104893.06375, 196022.244094),
            (104002.076625, 194168.3415, 105784.050875, 197876.146688)
        )
        assert p.id == ('1154/02C000')
        assert p.sectie.id == 'A'
        assert p.capatype == 'capaty'
        assert p.cashkey == 'cashkey'
        assert p.centroid == (104893.06375, 196022.244094)
        assert p.bounding_box == (104002.076625, 194168.3415, 105784.050875, 197876.146688)
        assert p.capakey == str(p)
        assert "Perceel('1154/02C000', Sectie('A', Afdeling(46013)), '40613A1154/02C000', '40613_A_1154_C_000_02')" == repr(p)

    def test_check_gateway_not_set(self):
        p = Perceel(
            '1154/02C000', Sectie('A', Afdeling(46013)),
            '40613A1154/02C000', '40613_A_1154_C_000_02'
        )
        with pytest.raises(RuntimeError):
            p.check_gateway()

    def test_clear_gateway(self, capakey_gateway):
        p = Perceel(
            '1154/02C000', Sectie('A', Afdeling(46013)),
            '40613A1154/02C000', '40613_A_1154_C_000_02'
        )
        p.set_gateway(capakey_gateway)
        p.check_gateway()
        p.sectie.check_gateway()
        p.clear_gateway()
        with pytest.raises(RuntimeError):
            p.sectie.check_gateway()
            p.check_gateway()


    @pytest.mark.skipif(
        not pytest.config.getoption('--capakey-integration'),
        reason = 'No CAPAKEY Integration tests required'
    )
    def test_lazy_load(self, capakey_gateway):
        p = Perceel(
            '1154/02C000', Sectie('A', Afdeling(46013)),
            '46013A1154/02C000', '46013_A_1154_C_000_02',
            gateway=capakey_gateway
        )
        assert p.id == '1154/02C000'
        assert p.sectie.id == 'A'
        assert p.sectie.afdeling.id == 46013
        assert not p.capatype == None
        assert not p.cashkey == None
        assert not p.centroid == None
        assert not p.bounding_box == None

    def test_parse_capakey(self):
        p = Perceel(
            '1154/02C000', Sectie('A', Afdeling(46013)),
            '46013A1154/02C000', '46013_A_1154_C_000_02'
        )
        assert p.grondnummer == '1154'
        assert p.bisnummer == '02'
        assert p.exponent == 'C'
        assert p.macht == '000'

    def test_parse_capakey_other_sectie(self):
        p = Perceel(
            '1154/02C000', Sectie('F', Afdeling(46013)),
            '46013F1154/02C000', '46013_F_1154_C_000_02'
        )
        assert p.grondnummer == '1154'
        assert p.bisnummer == '02'
        assert p.exponent == 'C'
        assert p.macht =='000'

    def test_parse_invalid_capakey(self):
        with pytest.raises(ValueError):
            Perceel(
                '1154/02C000', Sectie('A', Afdeling(46013)),
                '46013_A_1154_C_000_02',
                '46013A1154/02C000',
            )
