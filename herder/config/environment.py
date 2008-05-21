"""Pylons environment configuration"""
import os
import logging

from pylons import config
import sqlalchemy as sa
from sqlalchemy import engine_from_config

from sqlalchemymanager import SQLAlchemyManager

import herder.lib.app_globals as app_globals
import herder.lib.helpers
from herder.config.routing import make_map
from herder import model

log = logging.getLogger(__name__)

CONTEXT_ROLES = ('administer', 'translate', )

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

    # Customize templating options via this variable
    tmpl_options = config['buffet.template_options']

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
    config['pylons.g'].sa_engine = engine = \
        sa.engine_from_config(config, "sqlalchemy.")
    model.init_model(engine)

