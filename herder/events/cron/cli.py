import optparse

from herder import events
from herder.events import cron

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
        events.handle(cron.events.HerderMonthlyEvent())

    if opts.weekly:
        events.handle(cron.events.HerderWeeklyEvent())

    if opts.daily:
        events.handle(cron.events.HerderDailyEvent())

