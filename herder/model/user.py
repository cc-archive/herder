import sqlalchemy as sa
from sqlalchemy import orm
import random

from herder.model import meta

t_user = sa.Table("user", meta.metadata,
                      sa.Column('user_id', sa.types.Integer, primary_key = True, autoincrement = True),
                      sa.Column('user_name', sa.types.Unicode(255), nullable = False, unique = True),
                      sa.Column('salt', sa.types.String(255), nullable = False),
                      sa.Column('hashed_salted_pw', sa.types.String(255), nullable = False),
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
    return sha.sha(raw_password + salt).hexdigest()
