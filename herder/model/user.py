import sqlalchemy as sa
from sqlalchemy import orm

from herder.model import meta

user_table = sa.Table("wtf_User", meta,
                      sa.Column('user_id', sa.types.Integer, primary_key = True, autoincrement = True),
                      sa.Column('user_name', sa.types.Unicode(255), nullable = False),
                      sa.Column('salt', sa.types.String(255), nullable = False),
                      sa.Column('hashed_salted_pw', sa.types.String(255), nullable = False),
                      )

class User(object):
    def __str(self):
        return self.user_name

orm.mapper(User, user_table, 
           order_by=[user_table.c.user_id.asc()])
