import os
import optparse
import textwrap
import logging

from babel.messages import pofile

from herder.scripts import resolve_config, init_environment

def sync():
    """
    Look for new strings in a given language ("en" by default) and create
    empty translations in other languages if they do not exist.
    """

    # set up the option parser
    parser = optparse.OptionParser(description=textwrap.dedent(sync.__doc__))

    parser.add_option('-d', '--domain', dest='domain',
                      help='Name of the translation domain to sync.')
    parser.add_option('-l', '--lang', dest='language',
                      help='Language to sync from; defaults to "en".')

    parser.add_option('-c', '--config', dest='config',
                      help='Path to application configuration to load.')

    parser.set_defaults(domain=None,
                        language='en',
                        config='development.ini')


    # parse the command line
    opts, args = parser.parse_args()

    # set up the environment
    init_environment(resolve_config(opts.config))
    from herder import model
    
    if opts.domain is None:
        raise Exception("You must specify a domain.")

    domain = model.Domain.by_name(opts.domain)
    source = domain.get_language(opts.language)

    # iterate over each message in the source
    for message in source:

        # iterate over the other languages
        for lang in domain:
            if lang.name == source.name:
                # nevermind
                continue

            if not message in lang:
                model.Message(lang, message.id).update(u'')


def make_po():
    """Generate PO file(s) for a given Domain."""


    # set up the option parser
    parser = optparse.OptionParser(description=textwrap.dedent(sync.__doc__))

    parser.add_option('-d', '--domain', dest='domain',
                      help='Name of the translation domain to sync.')
    parser.add_option('-l', '--lang', dest='languages',
                      help='Languages to generate.  Separate language codes '
                      'with a comma.  If omitted, all languages will be '
                      'generated.')
    parser.add_option('-o', '--output', dest='output',
                      help='Output directory; individual language '
                      'directories will be created as necessary.')

    parser.add_option('-c', '--config', dest='config',
                      help='Path to application configuration to load.')

    parser.set_defaults(domain=None,
                        language=None,
                        output=None,
                        config='development.ini')


    # parse the command line
    opts, args = parser.parse_args()

    # set up the environment
    init_environment(resolve_config(opts.config))
    from herder import model
    
    if None in (opts.domain, opts.output):
        raise Exception("You must specify a domain and output path.")

    domain = model.Domain.by_name(opts.domain)

    # get a list of Language objects to manipulate
    if opts.languages is None:
        langs = domain.languages
    else:
        langs = [domain.get_language(l.strip()) 
                 for l in opts.languages.split(',')]

    for l in langs:
        # convert each to a Babel catalog
        catalog = l.get_catalog()

        # make sure the target dir exists
        lang_dir = os.path.join(opts.output, l.lang)
        if not os.path.exists(lang_dir):
            os.mkdir(lang_dir)

        # write the PO file
        po_file = file(os.path.join(lang_dir, "%s.po" % domain.name), 'w')
        pofile.write_po(po_file, catalog)


