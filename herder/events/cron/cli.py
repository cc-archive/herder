import optparse

from herder.events import handle
from herder.events.cron import events

def cron():
    """Command line interface for triggering time-based Herder events."""

    # create the option parser for the command-line

    parser = optparse.OptionParser()

    parser.add_option('-m', '--monthly', dest='monthly',
                      action='store_true',
                      help='Run monthly events.')

    parser.add_option('-w', '--weekly', dest='weekly',
                      action='store_true',
                      help='Run weekly events.')

    parser.add_option('-r', '--hourly', dest='hourly',
                      action='store_true',
                      help='Run hourly events.')

    parser.set_defaults(monthly=False,
                        weekly=False,
                        daily=False)

    # parse the command line
    opts, args = parser.parse_args()

    # trigger specified events
    if opts.monthly:
        handle(events.HerderMonthlyEvent())
        # Well, for no reason that does nothing.
        import herder.events.cron.handlers
        herder.events.cron.handlers.monthly_status_reminders(None)

    if opts.weekly:
        handle(events.HerderWeeklyEvent())

    if opts.daily:
        handle(events.HerderDailyEvent())

