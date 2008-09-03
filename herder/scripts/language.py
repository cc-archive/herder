import optparse
from herder.scripts import resolve_config, init_environment

def get_optparser(help):
    """Construct an OptionParser for the language scripts."""

    parser = optparse.OptionParser(description=help)

    parser.add_option('-d', '--domain', dest='domain',
                      help='Name of the translation domain to manipulate.')
    parser.add_option('-l', '--lang', dest='language',
                      help='Language code to manipulate.')
    parser.add_option('-c', '--config', dest='config',
                      help='Path to application configuration to load.')

    parser.set_defaults(domain=None,
                        language=None,
                        config='development.ini')

    return parser

def add():
    """Command line entry point for adding a language to a domain."""

    # parse the command line
    help = "Add a new language to a domain."""

    opts, args = get_optparser(help).parse_args()

    # set up the environment
    init_environment(resolve_config(opts.config))
    from herder import model
    
    if None in (opts.domain, opts.language):
        raise Exception("You must specify the domain and language.")

    domain = model.Domain.by_name(opts.domain)
    new_language = domain.add_language(opts.language)

    print "Added new language %s in %s." % (
        new_language.name, new_language._message_store)
