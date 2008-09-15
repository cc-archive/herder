import zope.component

import handlers
from events import HerderEvent, MessageUpdateEvent

def handle(event):
    """Convenience method to dispatch events into the "real" event 
    handling mechanism."""

    return zope.component.handle(event)
