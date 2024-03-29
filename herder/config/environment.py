"""Pylons environment configuration"""
import os
import logging
import pkg_resources

from pylons import config
from sqlalchemy import engine_from_config

import herder.lib.app_globals as app_globals
import herder.lib.helpers
from herder.config.routing import make_map
from herder.model import init_model

log = logging.getLogger(__name__)

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """

    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='herder',
                    template_engine='mako', paths=paths)

    config['routes.map'] = make_map()
    config['pylons.g'] = app_globals.Globals()
    config['pylons.h'] = herder.lib.helpers

    # Setup SQLAlchemy database engine
    engine = engine_from_config(config, 'sqlalchemy.')
    init_model(engine)

    # Customize templating options via this variable
    tmpl_options = config['buffet.template_options']

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)


    # Call event registration code
    for entry_point in pkg_resources.iter_entry_points(
        'herder.register_handlers'):

        entry_point.load()()

