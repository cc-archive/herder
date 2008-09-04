import optparse
import textwrap

from herder.scripts import resolve_config, init_environment

def get_optparser(help):
    """Construct an OptionParser for the language scripts."""

    parser = optparse.OptionParser(description=textwrap.dedent(help))

    parser.add_option('-d', '--domain', dest='domain',
                      help='Name of the translation domain to manipulate.')
    parser.add_option('-l', '--lang', dest='language',
                      help='Language code(s) to remove from; separate '
                      'language codes with a comma.  If no language is '
                      'specified, the string will be removed from all '
                      'languages.')
    parser.add_option('-m', '--message', dest='msgid',
                      help='Message ID to remove.')

    parser.add_option('-c', '--config', dest='config',
                      help='Path to application configuration to load.')

    parser.set_defaults(domain=None,
                        language=None,
                        msgid=None,
                        config='development.ini')

    return parser

def remove():
    """Remove a string from one or more languages."""

    # parse the command line
    opts, args = get_optparser(remove.__doc__).parse_args()

    # set up the environment
    init_environment(resolve_config(opts.config))
    from herder import model
    
    if None in (opts.domain, opts.msgid):
        raise Exception("You must specify the domain and message ID.")

    domain = model.Domain.by_name(opts.domain)
    if opts.language is None:
        languages = domain.languages
    else:
        languages = [domain.get_language(l.strip()) 
                     for l in opts.language.split(',')]

    for lang in languages:
        if opts.msgid in lang:
            del lang[opts.msgid]

    print "Removed %s from languages %s in %s." % (
        opts.msgid, ", ".join([str(l) for l in languages]), str(domain))
