import zope.component
from herder.events import HerderEvent

class HerderCronEvent(HerderEvent):
    """A time-triggered event."""

class HerderMonthlyEvent(HerderCronEvent):
    """A time-triggered event, sent for actions which should occur 
    monthly."""

class HerderWeeklyEvent(HerderCronEvent):
    """A time-triggered event, sent for actions which should occur 
    monthly."""

class HerderDailyEvent(HerderCronEvent):
    """A time-triggered event, sent for actions which should occur 
    monthly."""
