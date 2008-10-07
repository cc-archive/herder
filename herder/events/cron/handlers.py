import zope.component
from herder.events.send_email import send_email
from herder.events.cron.events import HerderMonthlyEvent

@zope.component.adapter(HerderMonthlyEvent)
def monthly_status_reminders(event):
    return

# beenhere works around an issue with nosetest + Pylons,
# where the registration gets called once per test run it seems.
# See: http://code.creativecommons.org/issues/issue31

# fine, so only let it be run once.
def register(beenhere = []):
    """Register included event handlers."""
    if not beenhere:
        beenhere.append(beenhere) # hah
        # register basic logging handler
        zope.component.provideHandler(monthly_status_reminders)