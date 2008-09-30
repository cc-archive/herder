import zope.interface
import zope.component
from herder.events import MessageUpdateEvent
import re

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

class SameNumberOfDollarInterpolations:
    zope.component.adapts(MessageUpdateEvent)
    zope.interface.implements(IValidateEvent)

    def _find_interpolations(self, s, regex = re.compile(r'[$]{[a-zA-Z0-9_.]+}')):
        '''Find all the ${lol}-type things in s.
        I couldn't find a function for this in Babel or Python core.'''
        return regex.findall(s)

    def __init__(self, event):
        '''Slide the event for later analysis.'''
        self.event = event

    def validate(self):
        '''Check if the old and new string have different numbers of
        string interpolations, and if so return a string of a relevant
        error.'''
        old_interps = set(self._find_interpolations(self.event.old_value))
        new_interps = set(self._find_interpolations(self.event.new_value))

        only_in_new = set()
        only_in_old = set()

        for interp in old_interps:
            if interp not in new_interps:
                only_in_old.add(interp)

        for interp in new_interps:
            if interp not in old_interps:
                only_in_new.add(interp)

        messages = []
        if only_in_old:
            messages.append(
                "The new string is missing these template string(s): " + 
                ' '.join(only_in_old))
        if only_in_new:
            messages.append(
                "The new string has these spurious template string(s): " + 
                ' '.join(only_in_new))

        return ' '.join(messages)

zope.component.provideSubscriptionAdapter(NotEicarValidator)
zope.component.provideSubscriptionAdapter(SameNumberOfDollarInterpolations)

def validate(obj):
    return filter(None,
                  [adapter.validate()
                   for adapter in
                   zope.component.subscribers([obj], IValidateEvent)])
