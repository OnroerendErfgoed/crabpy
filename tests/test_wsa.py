# -*- coding: utf-8 -*-

import unittest

from suds.sax.element import Element

from crabpy.wsa import wsa


class ElementTests(unittest.TestCase):

    def testAction(self):
        from crabpy.wsa import Action
        a = Action('http://soap.test.org/test')
        act = Element('Action', ns=wsa)
        act.setText('http://soap.test.org/test')
        self.assertEqual(act, a.xml())

    def testTo(self):
        from crabpy.wsa import To
        t = To('http://ws.agiv.be/capakeyws/nodataset.asmx')
        to = Element('To', ns=wsa)
        to.setText('http://ws.agiv.be/capakeyws/nodataset.asmx')
        self.assertEqual(to, t.xml())

    def testMessageId(self):
        from crabpy.wsa import MessageID
        mid = MessageID()
        # Test that we have the correct element. Ignores content.
        messageid = Element('MessageID', ns=wsa)
        self.assertEqual(messageid, mid.xml())
