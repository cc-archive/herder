import sqlalchemy as sa
from sqlalchemy import orm

from herder.model import meta

t_pref = sa.Table("pref", meta.metadata,
                  sa.Column('pref_id', sa.types.Integer, primary_key = True, autoincrement = True),
                  sa.Column('user_id', sa.types.Integer, sa.ForeignKey("user.user_id"), nullable = False),
                  sa.Column('lang_id', meta.Unicode(255), nullable = False),
                  sa.Column('domain_id', meta.Unicode(255), nullable = False),
                  sa.Column('pref_name', meta.Unicode(255), nullable = False),
                  sa.Column('pref_value', sa.types.Boolean, nullable = False),

                  sa.UniqueConstraint('user_id', 'lang_id', 'domain_id', 'pref_name'),
                  
                  )

class Pref(object):
    pass

orm.mapper(Pref, t_pref)

def get_pref(user_id, lang_id, domain_id, pref_name):
    # Check if the pref exists
    all_prefs = meta.Session.query(Pref).filter_by(
        user_id=user_id, lang_id=lang_id, domain_id=domain_id, pref_name=pref_name).all()
    if all_prefs:
        assert len(all_prefs) == 1
        pref = all_prefs[0]
        return pref
    return None
    

def set_pref(user_id, lang_id, domain_id, pref_name, pref_value):
    pref = get_pref(user_id, lang_id, domain_id, pref_name)
    if pref is not None:
        pref.pref_value = pref_value
        return pref
    else:
        ret = Pref()
        ret.user_id=user_id
        ret.lang_id=lang_id
        ret.domain_id=domain_id
        ret.pref_name=pref_name
        ret.pref_value=pref_value
        meta.Session.save(ret)
        return ret
