# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

from suds.sax.element import Element

from ..wsa import wsa

class ElementTests(unittest.TestCase):

    def testAction(self):
        from crabpy.wsa import Action
        a = Action('http://soap.test.org/test')
        act = Element('Action', ns=wsa)
        act.setText('http://soap.test.org/test')
        self.assertEqual(act, a.xml())

