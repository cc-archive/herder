import sqlalchemy as sa
from sqlalchemy import orm
import random

from herder.model import meta

t_authorization = sa.Table("authorization", meta.metadata,
                      sa.Column('authorization_id', sa.types.Integer, primary_key = True, autoincrement = True),
                      sa.Column('user_id', sa.types.Integer, sa.ForeignKey("user.user_id"), nullable = False),
                      sa.Column('lang_id', sa.types.Unicode(255), nullable = False),
                      sa.Column('domain_id', sa.types.Unicode(255), nullable = False),
                      sa.Column('role_id', sa.types.Integer, sa.ForeignKey("role.role_id"), nullable = False),
                      )

class Authorization(object):
    pass

orm.mapper(Authorization, t_authorization)

