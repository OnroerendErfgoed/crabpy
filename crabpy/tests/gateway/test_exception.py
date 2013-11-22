# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa


class ExceptionTests(unittest.TestCase):

    def test_inheritance(self):
        from crabpy.gateway.exception import GatewayRuntimeException
        e = GatewayRuntimeException(
            'Something went wrong.',
            'soapfault'
        )
        self.assertEqual(e.soapfault, 'soapfault')
        self.assertEqual(e.message, 'Something went wrong.')
