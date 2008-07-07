import sqlalchemy as sa
from sqlalchemy import orm
import random

from herder.model import meta

t_role = sa.Table("role", meta.metadata,
                      sa.Column('role_id', sa.types.Integer, primary_key = True, autoincrement = True),
                      sa.Column('role_name', sa.types.Unicode(255), nullable = False, unique = True),
                      )

class Role(object):
    pass

orm.mapper(Role, t_role)
