import zope.component
from pylons import session

class HerderEvent(object):
    """Super class for all Herder Event objects."""

class MessageUpdateEvent(HerderEvent):

    @classmethod
    def with_message(cls, message, old_value, new_value):

        return cls(message.language.domain.name,
                   message.language.lang,
                   message.id, old_value, new_value)

    def __init__(self, domain_id, lang_id, message_id,
                 old_value, new_value, user_id = None):

        self.domain_id = domain_id
        self.lang_id = lang_id
        self.message_id = message_id
        self.old_value = unicode(old_value)
        self.new_value = unicode(new_value)
        if user_id is None:
            # Try to yank it out of the session
            self.user_id = session.get('_user_id')
        else:
            self.user_id = user_id

    def __unicode__(self):
        return u"%s: %s: %s updated from <%s> to <%s> by %d" % (
            self.domain_id, self.lang_id, self.message_id,
            self.old_value, self.new_value, self.user_id)
