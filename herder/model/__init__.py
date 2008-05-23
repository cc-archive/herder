from language import Language as DomainLanguage
from language import Language
from domain import Domain
from message import Message

from pylons import config
from sqlalchemy import Column, MetaData, Table, types
from sqlalchemy.orm import mapper
from sqlalchemy.orm import scoped_session, sessionmaker

import sqlalchemy as sa
from herder.model import meta
from sqlalchemy import orm
from sqlalchemy import types

def init_model(engine):
    """Call me at the beginning of the application.
       'engine' is a SQLAlchemy engine or connection, as returned by
       sa.create_engine, sa.engine_from_config, or engine.connect().
    """
    sm = orm.sessionmaker(autoflush=True, transactional=True, bind=engine)

    meta.engine = engine
    meta.Session = orm.scoped_session(sm)

from herder.model import user
