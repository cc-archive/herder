"""SQLAlchemy Metadata and Session object"""
from sqlalchemy import MetaData, String

__all__ = ['engine', 'metadata', 'Session']

# SQLAlchemy database engine.  Updated by model.init_model().
engine = None

# SQLAlchemy session manager.  Updated by model.init_model().
Session = None

# Global metadata. If you have multiple databases with overlapping table 
# names, you'll need a metadata for each database.
metadata = MetaData()

# Create our custom Unicode class, since the SQLAlchemy one is broken
# when using pysqlite 2.5.0 (but 2.4.0 works okay).  This works on both.
class Unicode(String):
    def __init__(self, size = None):
        super(Unicode, self).__init__(
            size, convert_unicode = False, assert_unicode = True)
