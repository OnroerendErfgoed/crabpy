# -*- coding: utf-8 -*-

import pytest

from crabpy.gateway.capakey import (
    Gemeente,
    Afdeling,
    Sectie,
    Perceel
)

@pytest.fixture(scope="function")
def capakey_rest_gateway():
    from crabpy.gateway.capakey import CapakeyRestGateway
    capakey_rest_gateway = CapakeyRestGateway(
        cache_config={
            'permanent.backend': 'dogpile.cache.memory',
            'permanent.expiration_time': 86400,
            'long.backend': 'dogpile.cache.memory',
            'long.expiration_time': 3600,
            'short.backend': 'dogpile.cache.memory',
            'short.expiration_time': 600,
        }
    )
    return capakey_rest_gateway

@pytest.mark.skipif(
    not pytest.config.getoption('--capakey-integration'),
    reason = 'No CAPAKEY Integration tests required'
)
class TestCapakeyRestCachedGateway:

    def test_cache_is_configured(self, capakey_rest_gateway):
        from dogpile.cache.backends.memory import MemoryBackend
        assert isinstance(
            capakey_rest_gateway.caches['permanent'].backend,
            MemoryBackend
        )
        assert capakey_rest_gateway.caches['permanent'].is_configured

    def test_list_gemeenten(self, capakey_rest_gateway):
        res = capakey_rest_gateway.list_gemeenten()
        assert isinstance(res, list)
        assert capakey_rest_gateway.caches['permanent'].get('list_gemeenten_rest#1') == res

    def test_list_gemeenten_different_sort(self, capakey_rest_gateway):
        res = capakey_rest_gateway.list_gemeenten(2)
        assert isinstance(res, list)
        assert capakey_rest_gateway.caches['permanent'].get('list_gemeenten_rest#2') == res
        from dogpile.cache.api import NO_VALUE
        assert capakey_rest_gateway.caches['permanent'].get('list_gemeenten_rest#1') == NO_VALUE

    def test_get_gemeente_by_id(self, capakey_rest_gateway):
        res = capakey_rest_gateway.get_gemeente_by_id(44021)
        assert isinstance(res, Gemeente)
        assert capakey_rest_gateway.caches['long'].get('get_gemeente_by_id_rest#44021') == res

    def test_list_afdelingen(self, capakey_rest_gateway):
        res = capakey_rest_gateway.list_kadastrale_afdelingen()
        assert isinstance(res, list)
        assert capakey_rest_gateway.caches['permanent'].get('list_afdelingen_rest') == res

    def test_list_afdelingen_by_gemeente(self, capakey_rest_gateway):
        g = capakey_rest_gateway.get_gemeente_by_id(44021)
        assert capakey_rest_gateway.caches['long'].get('get_gemeente_by_id_rest#44021') == g
        res = capakey_rest_gateway.list_kadastrale_afdelingen_by_gemeente(g)
        assert isinstance(res, list)
        assert capakey_rest_gateway.caches['permanent'].get('list_kadastrale_afdelingen_by_gemeente_rest#44021#1') == res

    def test_get_kadastrale_afdeling_by_id(self, capakey_rest_gateway):
        res = capakey_rest_gateway.get_kadastrale_afdeling_by_id(44021)
        assert isinstance(res, Afdeling)
        assert res.id == 44021
        assert isinstance(res.gemeente, Gemeente)
        assert res.gemeente.id == 44021
        assert capakey_rest_gateway.caches['long'].get('get_kadastrale_afdeling_by_id_rest#44021') == res

    def test_list_secties_by_afdeling_id(self, capakey_rest_gateway):
        res = capakey_rest_gateway.list_secties_by_afdeling(44021)
        assert isinstance(res, list)
        assert len(res) == 1
        assert capakey_rest_gateway.caches['long'].get('list_secties_by_afdeling_rest#44021') == res

    def test_get_sectie_by_id_and_afdeling(self, capakey_rest_gateway):
        a = capakey_rest_gateway.get_kadastrale_afdeling_by_id(44021)
        res = capakey_rest_gateway.get_sectie_by_id_and_afdeling('A', a)
        assert isinstance(res, Sectie)
        assert res.id == 'A'
        assert res.afdeling.id == 44021
        assert capakey_rest_gateway.caches['long'].get('get_sectie_by_id_and_afdeling_rest#A#44021') == res

    def test_list_percelen_by_sectie(self, capakey_rest_gateway):
        s = capakey_rest_gateway.get_sectie_by_id_and_afdeling('A', 44021)
        res = capakey_rest_gateway.list_percelen_by_sectie(s)
        assert isinstance(res, list)
        assert len(res) > 0
        assert capakey_rest_gateway.caches['short'].get('list_percelen_by_sectie_rest#44021#44021#A') == res

    def test_get_perceel_by_id_and_sectie(self, capakey_rest_gateway):
        s = capakey_rest_gateway.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = capakey_rest_gateway.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = capakey_rest_gateway.get_perceel_by_id_and_sectie(perc.id, s)
        assert isinstance(res, Perceel)
        assert res.sectie.id =='A'
        assert res.sectie.afdeling.id == 44021
        'get_perceel_by_id_and_sectie_rest#0001/00A000#A#44021'
        assert capakey_rest_gateway.caches['short'].get('get_perceel_by_id_and_sectie_rest#%s#A#44021' % perc.id) == res

    def test_get_perceel_by_capakey(self, capakey_rest_gateway):
        s = capakey_rest_gateway.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = capakey_rest_gateway.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = capakey_rest_gateway.get_perceel_by_capakey(perc.capakey)
        assert isinstance(res, Perceel)
        assert res.sectie.id == 'A'
        assert res.sectie.afdeling.id, 44021
        assert capakey_rest_gateway.caches['short'].get('get_perceel_by_capakey_rest#%s' % perc.capakey) == res

    def test_get_perceel_by_percid(self, capakey_rest_gateway):
        s = capakey_rest_gateway.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = capakey_rest_gateway.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = capakey_rest_gateway.get_perceel_by_percid(perc.percid)
        assert isinstance(res, Perceel)
        assert res.sectie.id == 'A'
        assert res.sectie.afdeling.id == 44021
        assert capakey_rest_gateway.caches['short'].get('get_perceel_by_capakey_rest#%s' % perc.capakey) == res

