# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from base64 import b64encode

import hashlib

from datetime import datetime

from suds.wsse import UsernameToken, wssens, wsuns

from suds.sax.element import Element

from suds.sax.date import DateTime



class UsernameDigestToken(UsernameToken):
    """
    Represents a basic I{UsernameToken} WS-Security token with password digest
    @ivar username: A username.
    @type username: str
    @ivar password: A password.
    @type password: str
    @ivar nonce: A set of bytes to prevent reply attacks.
    @type nonce: str
    @ivar created: The token created.
    @type created: L{datetime}

    @doc: http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0.pdf
    """

    def __init__(self, username=None, password=None):
        UsernameToken.__init__(
            self,
            username, 
            password
        )
        utc = UsernameToken.utc()
        utc = datetime(
            utc.year, utc.month, utc.day,
            utc.hour, utc.minute, utc.second,
            tzinfo=utc.tzinfo
        )
        self.setcreated(utc)
        self.setnonce()

    def setnonce(self, text=None):
        if text is None:
            s = []
            s.append(self.username)
            s.append(self.password)
            s.append(str(datetime.utcnow()))
            m = hashlib.md5()
            m.update(':'.join(s))
            self.raw_nonce = m.digest()
            self.nonce = b64encode(self.raw_nonce)
        else:
            self.nonce = text

    @staticmethod
    def _print_datetime(dt):
        return "%.4d-%.2d-%.2dT%.2d:%.2d:%.2dZ" % (
            dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second
        )

    def xml(self):
        usernametoken = Element('UsernameToken', ns=wssens)

        username = Element('Username', ns=wssens)
        username.setText(self.username)
        usernametoken.append(username)

        password = Element('Password', ns=wssens)
        s = hashlib.sha1()
        s.update(self.raw_nonce)
        s.update(self._print_datetime(self.created))
        s.update(self.password)
        password.setText(b64encode(s.digest()))
        password.set('Type', 'http://docs.oasis-open.org/wss/2004/01/'
                             'oasis-200401-wss-username-token-profile-1.0'
                             '#PasswordDigest')
        usernametoken.append(password)
        
        nonce = Element('Nonce', ns=wssens)
        nonce.setText(self.nonce)
        nonce.set('EncodingType', 'http://docs.oasis-open.org/wss/2004'
            '/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary')
        usernametoken.append(nonce)

        created = Element('Created', ns=wsuns)
        created.setText(self._print_datetime(self.created))
        usernametoken.append(created)

        return usernametoken


