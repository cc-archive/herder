"""Setup the herder application"""
import logging

from paste.deploy import appconfig
from pylons import config

from herder.config.environment import load_environment, CONTEXT_ROLES
import herder

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup herder here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)

    from herder.model import meta
    log.info("Creating tables")
    meta.metadata.create_all(bind=meta.engine)
    log.info("Successfully setup tables")

    admin_role = herder.model.role.Role()
    admin_role.role_name = 'administer'
    translate_role = herder.model.role.Role()
    translate_role.role_name = 'translate'
    herder.model.meta.Session.save(admin_role)
    herder.model.meta.Session.save(translate_role)
    herder.model.meta.Session.commit()
