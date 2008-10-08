import optparse

from herder.events import handle
from herder.events.cron import events
from herder.scripts import resolve_config, init_environment

def cron(args = None):
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

    parser.add_option('-c', '--config', dest='config',
                      help='Path to application configuration to load.')


    parser.set_defaults(monthly=False,
                        weekly=False,
                        daily=False)

    # parse the command line
    opts, args = parser.parse_args(args)

    # set up the environment
    init_environment(resolve_config(opts.config))

    # trigger specified events
    if opts.monthly:
        handle(events.HerderMonthlyEvent())

    if opts.weekly:
        handle(events.HerderWeeklyEvent())

    if opts.daily:
        handle(events.HerderDailyEvent())

