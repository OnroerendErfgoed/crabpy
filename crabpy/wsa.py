"""
This module contains utiltiy functions for using WSA with SOAP services.

.. versionadded:: 0.1.0
"""

import uuid

from suds.sax.element import Element
from suds.sudsobject import Object

wsa = ("wsa", "http://schemas.xmlsoap.org/ws/2004/08/addressing")


class Action(Object):
    """
    Assist in rendering a WSA:Action element.
    """

    def __init__(self, action):
        Object.__init__(self)
        self.action = action

    def xml(self):
        action = Element("Action", ns=wsa)
        action.setText(self.action)
        return action


class MessageID(Object):
    """
    Assist in rendering a WSA:MessageID element.
    """

    def xml(self):
        messageid = Element("MessageID", ns=wsa)
        messageid.setText("uuid: " + str(uuid.uuid4()))
        return messageid


class To(Object):
    """
    Assist in rendering a WSA:To element.
    """

    def __init__(self, location):
        Object.__init__(self)
        self.location = location

    def xml(self):
        to = Element("To", ns=wsa)
        to.setText(self.location)
        return to
