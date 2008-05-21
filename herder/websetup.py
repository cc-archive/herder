"""Setup the herder application"""
import logging

from paste.deploy import appconfig
from pylons import config

from sqlalchemymanager import SQLAlchemyManager

from herder.config.environment import load_environment, CONTEXT_ROLES
from herder.model import setup_model

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup herder here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)

    manager = SQLAlchemyManager(None, conf.local_conf, 
        [setup_model])
    manager.create_all()

    connection = manager.engine.connect()
    session = manager.session_maker(bind=connection)
