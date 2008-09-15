import logging

import zope.component
from herder.events.events import HerderEvent

@zope.component.adapter(HerderEvent)
def logging_handler(event):
    print event

# beenhere works around an issue with nosetests + Pylons,
# where the registration gets called once per test run it seems.
# See: http://code.creativecommons.org/issues/issue31

# fine, so only let it be run once.
beenhere = False
def register():
    """Register included event handlers."""
    global beenhere
    if not beenhere:
        beenhere = True
        # register basic logging handler
        zope.component.provideHandler(logging_handler)
