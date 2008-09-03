"""Setup the herder application"""
import logging

from paste.deploy import appconfig
from pylons import config

from herder.config.environment import load_environment
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

    bureau_role = herder.model.role.Role()
    bureau_role.role_name = 'bureaucrat'
    translator_role = herder.model.role.Role()
    translator_role.role_name = 'translator'
    herder.model.meta.Session.save(bureau_role)
    herder.model.meta.Session.save(translator_role)
    herder.model.meta.Session.commit()
