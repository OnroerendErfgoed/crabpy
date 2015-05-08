# -*- coding: utf-8 -*-

import pytest

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

@pytest.fixture(scope="function")
def capakey_gateway(capakey):
    from crabpy.gateway.capakey import CapakeyGateway
    capakey_gateway = CapakeyGateway(
        capakey,
        cache_config={
            'permanent.backend': 'dogpile.cache.memory',
            'permanent.expiration_time': 86400,
            'long.backend': 'dogpile.cache.memory',
            'long.expiration_time': 3600,
            'short.backend': 'dogpile.cache.memory',
            'short.expiration_time': 600,
        }
    )
    return capakey_gateway

@pytest.mark.skipif(
    not pytest.config.getoption('--capakey-integration'),
    reason = 'No CAPAKEY Integration tests required'
)
class TestCapakeyCachedGateway:

    def test_cache_is_configured(self, capakey_gateway):
        from dogpile.cache.backends.memory import MemoryBackend
        assert isinstance(
            capakey_gateway.caches['permanent'].backend,
            MemoryBackend
        )
        assert capakey_gateway.caches['permanent'].is_configured

    def test_list_gemeenten(self, capakey_gateway):
        res = capakey_gateway.list_gemeenten()
        assert isinstance(res, list)
        assert capakey_gateway.caches['permanent'].get('ListAdmGemeenten#1') == res

    def test_list_gemeenten_different_sort(self, capakey_gateway):
        res = capakey_gateway.list_gemeenten(2)
        assert isinstance(res, list)
        assert capakey_gateway.caches['permanent'].get('ListAdmGemeenten#2') == res
        from dogpile.cache.api import NO_VALUE
        assert capakey_gateway.caches['permanent'].get('ListAdmGemeenten#1') == NO_VALUE

    def test_get_gemeente_by_id(self, capakey_gateway):
        res = capakey_gateway.get_gemeente_by_id(44021)
        assert isinstance(res, Gemeente)
        assert capakey_gateway.caches['long'].get('GetAdmGemeenteByNiscode#44021') == res

    def test_list_afdelingen(self, capakey_gateway):
        res = capakey_gateway.list_kadastrale_afdelingen()
        assert isinstance(res, list)
        assert capakey_gateway.caches['permanent'].get('ListKadAfdelingen#1') == res

    def test_list_afdelingen_by_gemeente(self, capakey_gateway):
        g = capakey_gateway.get_gemeente_by_id(44021)
        assert capakey_gateway.caches['long'].get('GetAdmGemeenteByNiscode#44021') == g
        res = capakey_gateway.list_kadastrale_afdelingen_by_gemeente(g)
        assert isinstance(res, list)
        assert capakey_gateway.caches['permanent'].get('ListKadAfdelingenByNiscode#44021#1') == res

    def test_get_kadastrale_afdeling_by_id(self, capakey_gateway):
        res = capakey_gateway.get_kadastrale_afdeling_by_id(44021)
        assert isinstance(res, Afdeling)
        assert res.id == 44021
        assert isinstance(res.gemeente, Gemeente)
        assert res.gemeente.id == 44021
        assert capakey_gateway.caches['long'].get('GetKadAfdelingByKadAfdelingcode#44021') == res

    def test_list_secties_by_afdeling_id(self, capakey_gateway):
        res = capakey_gateway.list_secties_by_afdeling(44021)
        assert isinstance(res, list)
        assert (len(res), 1)
        assert capakey_gateway.caches['long'].get('ListKadSectiesByKadAfdelingcode#44021') == res

    def test_get_sectie_by_id_and_afdeling(self, capakey_gateway):
        a = capakey_gateway.get_kadastrale_afdeling_by_id(44021)
        res = capakey_gateway.get_sectie_by_id_and_afdeling('A', a)
        assert isinstance(res, Sectie)
        assert res.id == 'A'
        assert res.afdeling.id == 44021
        assert capakey_gateway.caches['long'].get('GetKadSectieByKadSectiecode#44021#A') == res

    def test_list_percelen_by_sectie(self, capakey_gateway):
        s = capakey_gateway.get_sectie_by_id_and_afdeling('A', 44021)
        res = capakey_gateway.list_percelen_by_sectie(s)
        assert isinstance(res, list)
        assert len(res) > 0
        assert capakey_gateway.caches['short'].get('ListKadPerceelsnummersByKadSectiecode#44021#A#1') == res

    def test_get_perceel_by_id_and_sectie(self, capakey_gateway):
        s = capakey_gateway.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = capakey_gateway.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = capakey_gateway.get_perceel_by_id_and_sectie(perc.id, s)
        assert isinstance(res, Perceel)
        assert res.sectie.id =='A'
        assert res.sectie.afdeling.id == 44021
        assert capakey_gateway.caches['short'].get('GetKadPerceelsnummerByKadPerceelsnummer#44021#A#%s' % perc.id) == res

    def test_get_perceel_by_capakey(self, capakey_gateway):
        s = capakey_gateway.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = capakey_gateway.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = capakey_gateway.get_perceel_by_capakey(perc.capakey)
        assert isinstance(res, Perceel)
        assert res.sectie.id == 'A'
        assert res.sectie.afdeling.id, 44021
        assert capakey_gateway.caches['short'].get('GetKadPerceelsnummerByCaPaKey#%s' % perc.capakey) == res

    def test_get_perceel_by_percid(self, capakey_gateway):
        s = capakey_gateway.get_sectie_by_id_and_afdeling('A', 44021)
        percelen = capakey_gateway.list_percelen_by_sectie(s)
        perc = percelen[0]
        res = capakey_gateway.get_perceel_by_percid(perc.percid)
        assert isinstance(res, Perceel)
        assert res.sectie.id == 'A'
        assert res.sectie.afdeling.id == 44021
        assert capakey_gateway.caches['short'].get('GetKadPerceelsnummerByPERCID#%s' % perc.percid) == res
