# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest

from crabpy.client import (
    crab_factory,
    capakey_factory,
    capakey_request
)

@pytest.mark.skipif(
    not pytest.config.getoption('--crab-integration'),
    reason='No CRAB Integration tests required'
)
class TestCrabClient:

    def setup_method(self, method):
        self.crab = crab_factory()

    def teardown_method(self, method):
        self.crab = None

    def test_override_wsdl(self):
        wsdl = "http://crab.agiv.be/wscrab/wscrab.svc?wsdl"
        self.crab = crab_factory(
            wsdl=wsdl
        )
        assert self.crab.wsdl.url == wsdl

    def test_list_gemeenten(self):
        res = self.crab.service.ListGemeentenByGewestId(2)
        assert len(res) > 0


class TestCapakeyClient:

    def test_user_and_password_must_be_set(self):
        with pytest.raises(ValueError):
            capakey_factory()

    @pytest.mark.skipif(
        not pytest.config.getoption('--capakey-soap-integration'),
        reason = 'No CAPAKEY Integration tests required'
    )
    def test_override_wsdl(self, request):
        wsdl = "http://ws.agiv.be/capakeyws/nodataset.asmx?WSDL"
        self.capakey = capakey_factory(
            wsdl=wsdl,
            user=request.config.getoption('--capakey-soap-user'),
            password=request.config.getoption('--capakey-soap-password')
        )
        assert self.capakey.wsdl.url == wsdl

    @pytest.mark.skipif(
        not pytest.config.getoption('--capakey-soap-integration'),
        reason = 'No CAPAKEY Integration tests required'
    )
    def test_list_gemeenten(self, capakey):
        res = capakey_request(capakey, 'ListAdmGemeenten', 1)
        assert len(res) > 0
