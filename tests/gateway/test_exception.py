# -*- coding: utf-8 -*-

import unittest


class ExceptionTests(unittest.TestCase):

    def test_inheritance(self):
        from crabpy.gateway.exception import GatewayRuntimeException
        e = GatewayRuntimeException(
            'Something went wrong.',
            'soapfault'
        )
        self.assertEqual(e.soapfault, 'soapfault')
        self.assertEqual(e.message, 'Something went wrong.')
