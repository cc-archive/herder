"""Setup the herder application"""
import logging

from paste.deploy import appconfig
from pylons import config

from herder.config.environment import load_environment
import herder
import herder.controllers.account

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars,
                 bureaucrat_username = None, bureaucrat_password = None):
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

    if bureaucrat_username is None:
        bureaucrat_username = raw_input(
            'Hey there.  What username do you want for your bureaucrat user? > ')
        bureaucrat_realname = raw_input(
            'Great.  What is the actual name of this person? > ')

    if bureaucrat_password is None:
        bureaucrat_password = herder.model.user.random_alphanum()
    
    # make the new bureaucrat user
    new_user = herder.model.user.User()
    new_user.user_name = unicode(bureaucrat_username)
    new_user.salt = herder.model.user.random_alphanum()
    new_user.hashed_salted_pw = herder.model.user.hash_with_salt(
        salt=new_user.salt,
        raw_password=bureaucrat_password)
    new_user.human_name = bureaucrat_realname
    herder.model.meta.Session.save(new_user)

    # Flush the session...
    herder.model.meta.Session.commit()

    # and bless him with magical powers
    herder.controllers.account.bless_user(new_user)

    # And say what we've done.
    print 'Congratulations.  Your password is:', bureaucrat_password


    
