"""
This module adds a :class:`UsernameDigestToken` for use with SOAP services.

.. versionadded:: 0.2.0
"""


import hashlib
from base64 import b64encode
from datetime import datetime

from suds.sax.element import Element
from suds.wsse import UsernameToken
from suds.wsse import wssens
from suds.wsse import wsuns


class UsernameDigestToken(UsernameToken):
    """
    Represents a basic WS-Security token with password digest
    """

    def __init__(self, username=None, password=None):
        UsernameToken.__init__(self, username, password)
        utc = UsernameToken.utc()
        utc = datetime(
            utc.year,
            utc.month,
            utc.day,
            utc.hour,
            utc.minute,
            utc.second,
            tzinfo=utc.tzinfo,
        )
        self.setcreated(utc)
        self.setnonce()

    def setnonce(self, text=None):
        if text is None:
            s = []
            s.append(self.username.encode("utf-8"))
            s.append(self.password.encode("utf-8"))
            s.append(str(datetime.utcnow()).encode("utf-8"))
            m = hashlib.md5()
            m.update(b":".join(s))
            self.nonce = m.hexdigest().encode("utf-8")
        else:
            self.nonce = text

    @staticmethod
    def _print_datetime(dt):
        return "%.4d-%.2d-%.2dT%.2d:%.2d:%.2dZ" % (
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
        )

    def xml(self):
        usernametoken = Element("UsernameToken", ns=wssens)

        username = Element("Username", ns=wssens)
        username.setText(self.username)
        usernametoken.append(username)

        password = Element("Password", ns=wssens)
        s = hashlib.sha1()
        s.update(self.nonce)
        s.update(self._print_datetime(self.created).encode("utf-8"))
        s.update(self.password.encode("utf-8"))
        password.setText(b64encode(s.digest()).decode("utf-8"))
        password.set(
            "Type",
            "http://docs.oasis-open.org/wss/2004/01/"
            "oasis-200401-wss-username-token-profile-1.0"
            "#PasswordDigest",
        )
        usernametoken.append(password)

        nonce = Element("Nonce", ns=wssens)
        nonce.setText(b64encode(self.nonce).decode("utf-8"))
        nonce.set(
            "EncodingType",
            "http://docs.oasis-open.org/wss/2004"
            "/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary",
        )
        usernametoken.append(nonce)

        created = Element("Created", ns=wsuns)
        created.setText(self._print_datetime(self.created))
        usernametoken.append(created)

        return usernametoken
