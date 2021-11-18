import unittest

from crabpy.wsse import UsernameDigestToken

from base64 import b64encode

from suds.wsse import wssens

from suds.sax.element import Element


class UsernameDigestTokenTests(unittest.TestCase):

    def setUp(self):
        self.token = UsernameDigestToken('myself', 'mypassword')

    def tearDown(self):
        self.token = None

    def test_simple(self):
        self.assertIsInstance(self.token, UsernameDigestToken)
        xml = self.token.xml()
        self.assertIsInstance(xml, Element)
        self.assertIsInstance(xml.getChild('Username', ns=wssens), Element)
        self.assertIsInstance(xml.getChild('Password', ns=wssens), Element)
        self.assertIsInstance(xml.getChild('Nonce', ns=wssens), Element)

    def test_set_custom_nonce(self):
        self.assertIsInstance(self.token, UsernameDigestToken)
        self.token.setnonce(b'NONCE')
        xml = self.token.xml()
        self.assertIsInstance(xml, Element)
        self.assertIsInstance(xml.getChild('Username', ns=wssens), Element)
        self.assertIsInstance(xml.getChild('Password', ns=wssens), Element)
        self.assertIsInstance(xml.getChild('Nonce', ns=wssens), Element)
        self.assertEqual(
            xml.getChild('Nonce', ns=wssens).getText(),
            b64encode(b'NONCE').decode('utf-8')
        )
