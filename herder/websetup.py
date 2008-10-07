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
    if 'first_bureaucrat.username' in conf.local_conf:
        bureaucrat_username = unicode(conf.local_conf['first_bureaucrat.username'])
    else:
        bureaucrat_username = unicode(raw_input(
            'Hey there.  What username do you want for your bureaucrat user? > '))
    if 'first_bureaucrat.realname' in conf.local_conf:
        bureaucrat_realname = unicode(conf.local_conf['first_bureaucrat.realname'])
    else:
        bureaucrat_realname = unicode(raw_input(
            'Great.  What is the actual name of this person? > '))

    if 'first_bureaucrat.password' in conf.local_conf:
        bureaucrat_password = unicode(conf.local_conf['first_bureaucrat.password'])
    else:
        bureaucrat_password = herder.model.user.random_alphanum()

    if 'first_bureaucrat.email' in conf.local_conf:
        bureaucrat_email = conf.local_conf['first_bureaucrat.email']
    else:
        bureaucrat_email = raw_input(
            'What email address for the first bureaucrat user? > ')
    
    # make the new bureaucrat user
    new_user = herder.model.user.User()
    new_user.user_name = unicode(bureaucrat_username)
    new_user.salt = herder.model.user.random_alphanum()
    new_user.hashed_salted_pw = herder.model.user.hash_with_salt(
        salt=new_user.salt,
        raw_password=bureaucrat_password)
    new_user.human_name = bureaucrat_realname
    new_user.email = bureaucrat_email
    herder.model.meta.Session.save(new_user)

    # Flush the session...
    herder.model.meta.Session.commit()

    # and bless him with magical powers
    herder.controllers.account.bless_user(new_user)

    # And say what we've done.
    print 'Congratulations.  Your password is:', bureaucrat_password


    
