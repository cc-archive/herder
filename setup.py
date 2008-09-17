from setuptools import setup, find_packages

setup(
    name='herder',
    version="8.3",
    #description='',
    #author='',
    #author_email='',
    #url='',
    install_requires=['setuptools',
                      'pudge',
                       'Paste>=dev',
                      'buildutils',
#                      'BeautifulSoup',
                      'Pygments',
                      'feedparser',
                      'WebHelpers>0.3',
                      'PyRSS2Gen',
                      'Pylons>=0.9.6', 
                      'Babel',
                      'MiniMock',
                      'jsonlib',
                      'SQLAlchemy>=0.4.0,<=0.4.99',
                      'SQLAlchemyManager',
                      'pysqlite',
                      'nose',
                      'jToolkit',
                      'selenium',
                      'zope.component'
                      ],

    dependency_links=[
                      'svn://lesscode.org/pudge/trunk#egg=pudge-dev',
                      'svn://lesscode.org/buildutils/trunk#egg=buildutils-dev',
                      'http://labs.creativecommons.org/~paulproteus/eggs/',
                      'http://www.dalkescientific.com/Python/PyRSS2Gen-1.0.0.tar.gz#egg=PyRSS2Gen',
                      ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'herder': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors = {'herder': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', None),
    #        ('public/**', 'ignore', None)]},
    entry_points="""
    [paste.app_factory]
    main = herder.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [herder.register_handlers]
    herder = herder.events.handlers:register

    [console_scripts]
    sync     = herder.scripts.domain:sync
    addlang  = herder.scripts.language:add
    rmstring = herder.scripts.message:remove
    make_po  = herder.scripts.domain:make_po
    cron     = herder.events.cron.cli:cron
    """,
)
