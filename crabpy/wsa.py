from suds.sudsobject import Object
from suds.sax.element import Element

import uuid

wsa = ('wsa', 'http://www.w3.org/2005/08/addressing')

class Action(Object):
    def __init__(self, action):
        Object.__init__(self)
        self.action = action
                    
    def xml(self):
        action = Element('Action', ns=wsa)
        action.setText(self.action)
        return action
                                                
class MessageID(Object):
    def xml(self):
        messageid = Element('MessageID', ns=wsa)
        messageid.setText('uuid: ' + str(uuid.uuid4()))
        return messageid
                
class To(Object):
    def __init__(self, location):
        Object.__init__(self)
        self.location = location
                        
    def xml(self):
        to = Element('To', ns=wsa)
        to.setText(self.location)
        return to
