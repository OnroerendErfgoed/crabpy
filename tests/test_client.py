# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest

from crabpy.client import (
    crab_factory,
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
