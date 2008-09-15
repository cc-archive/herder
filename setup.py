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
                      'buildutils',
                      'BeautifulSoup',
                      'Pygments',
                      'WebHelpers>0.3',
                      'Pylons>=0.9.6', 
                      'Babel',
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
    """,
)
