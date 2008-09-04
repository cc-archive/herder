import logging

import zope.component
from herder.events.events import HerderEvent


@zope.component.adapter(HerderEvent)
def logging_handler(event):
    print event

zope.component.provideHandler(logging_handler)
