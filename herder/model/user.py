import sqlalchemy as sa
from sqlalchemy import orm

from herder.model import meta

t_user = sa.Table("wtf_User", meta.metadata,
                      sa.Column('user_id', sa.types.Integer, primary_key = True, autoincrement = True),
                      sa.Column('user_name', sa.types.Unicode(255), nullable = False),
                      sa.Column('salt', sa.types.String(255), nullable = False),
                      sa.Column('hashed_salted_pw', sa.types.String(255), nullable = False),
                      )

class User(object):
    pass

orm.mapper(User, t_user)
