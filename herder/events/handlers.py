import logging

import zope.component
from herder.events.events import HerderEvent

@zope.component.adapter(HerderEvent)
def logging_handler(event):
    print event

def register():
    """Register included event handlers."""

    # register basic logging handler
    zope.component.provideHandler(logging_handler)
