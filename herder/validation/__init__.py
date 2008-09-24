import zope.interface
import zope.component
from herder.events import MessageUpdateEvent

class IValidateEvent(zope.interface.Interface):
    def validate():
        '''Determine whether the event passed in at initialization time.
       
        Return a string describing a validation problem.
        An empty string is returned to indicate that the
        object is valid.
        '''

## FIXME: Use a setuptools entrypoint to discover which 

class NotEicarValidator:
    zope.component.adapts(MessageUpdateEvent)
    zope.interface.implements(IValidateEvent)

    def __init__(self, event):
        self.event = event

    def validate(self):
        if self.event.new_value == 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*':
            return 'ZOMG INFEKTED'
        return ''

zope.component.provideSubscriptionAdapter(NotEicarValidator)

def validate(obj):
    return filter(None,
                  [adapter.validate()
                   for adapter in
                   zope.component.subscribers([obj], IValidateEvent)])
