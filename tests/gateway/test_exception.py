# -*- coding: utf-8 -*-

import pytest


class TestException:

    def test_inheritance(self):
        from crabpy.gateway.exception import GatewayRuntimeException
        e = GatewayRuntimeException(
            'Something went wrong.',
            'soapfault'
        )
        assert e.soapfault == 'soapfault'
        assert e.message =='Something went wrong.'
