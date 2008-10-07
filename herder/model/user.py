import sqlalchemy as sa
from sqlalchemy import orm
import random

from herder.model import meta

t_user = sa.Table("user", meta.metadata,
                      sa.Column('user_id', sa.types.Integer, primary_key = True, autoincrement = True),
                      sa.Column('user_name', meta.Unicode(255), nullable = False, unique = True),
                      sa.Column('salt', meta.Unicode(255), nullable = False),
                      sa.Column('hashed_salted_pw', meta.Unicode(255), nullable = False),
                      sa.Column('human_name', meta.Unicode(255), nullable = False),
                      sa.Column('email', meta.Unicode(255), nullable = False),
                      )

class User(object):
    pass

orm.mapper(User, t_user)

def random_alphanum(length = 12):
    source = 'abcdefghijklmnopqrstuvxyz' + '0123456789'
    ret = ''
    for n in range(length):
        ret += random.choice(source)
    return ret

import sha
def hash_with_salt(salt, raw_password):
    return sha.sha(salt + raw_password + salt).hexdigest()

import md5
def hash_oldskool(raw_password):
    return md5.md5(raw_password).hexdigest()

def upgrade_password(db_user, raw_password):
    ''' NOTE: This does not flush the session, or even save your
    object for you.

    It does modify db_user, so you should save and flush yourself.'''
    assert db_user.hashed_salted_pw == hash_oldskool(raw_password)
    db_user.salt = random_alphanum()
    db_user.hashed_salted_pw = hash_with_salt(db_user.salt, raw_password)

def make_md5_user(user_name, hashed, email, human_name):
    new_user = User()
    new_user.user_name = unicode(user_name)
    new_user.salt = 'ignored'
    new_user.hashed_salted_pw = hashed
    new_user.human_name = unicode(human_name)
    new_user.email = unicode(email)
    return new_user

    
