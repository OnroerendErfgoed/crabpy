# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest
import os
from paste.deploy.loadwsgi import appconfig

from crabpy.client import (
    crab_factory,
    capakey_factory,
    capakey_request
)
import py
TEST_DIR = os.path.dirname(__file__)
settings = appconfig('config:' + os.path.join(TEST_DIR, '../' + py.test.config.option.__dict__['inifilename']))

def run_crab_integration_tests():
    from tests import as_bool
    try:
        return as_bool(settings['crab_run_integration_tests'])
    except KeyError:  # pragma NO COVER
        return False


def run_capakey_integration_tests():
    from tests import as_bool
    try:
        return as_bool(settings['capakey_run_integration_tests'])
    except KeyError:  # pragma NO COVER
        return False


class CrabClientTests(unittest.TestCase):

    def setUp(self):
        self.crab = crab_factory()

    def tearDown(self):
        self.crab = None

    @unittest.skipUnless(
        run_crab_integration_tests(),
        'No CRAB Integration tests required'
    )
    def test_override_wsdl(self):
        wsdl = "http://crab.agiv.be/wscrab/wscrab.svc?wsdl"
        self.crab = crab_factory(
            wsdl=wsdl
        )
        self.assertEqual(self.crab.wsdl.url, wsdl)

    @unittest.skipUnless(
        run_crab_integration_tests(),
        'No CRAB Integration tests required'
    )
    def test_list_gemeenten(self):
        res = self.crab.service.ListGemeentenByGewestId(2)
        self.assertGreater(len(res), 0)


@unittest.skipUnless(
    run_capakey_integration_tests(),
    'No CAPAKEY Integration tests required'
)
class CapakeyClientTests(unittest.TestCase):

    def setUp(self):
        self.capakey = capakey_factory(
            user=settings['capakey_user'],
            password=settings['capakey_password']
        )

    def tearDown(self):
        self.capakey = None

    def test_user_and_password_must_be_set(self):
        self.assertRaises(ValueError, capakey_factory)

    def test_override_wsdl(self):
        wsdl = "http://ws.agiv.be/capakeyws/nodataset.asmx?WSDL"
        self.capakey = capakey_factory(
            wsdl=wsdl,
            user=settings['capakey_user'],
            password=settings['capakey_password']
        )
        self.assertEqual(self.capakey.wsdl.url, wsdl)

    def test_list_gemeenten(self):
        res = capakey_request(self.capakey, 'ListAdmGemeenten', 1)
        self.assertGreater(len(res), 0)
