import zope.component

class HerderEvent(object):
    """Super class for all Herder Event objects."""

class MessageUpdateEvent(HerderEvent):

    @classmethod
    def with_message(cls, message):

        return cls(message.language.domain.name,
                   message.language.lang,
                   message.id)

    def __init__(self, domain_id, lang_id, message_id):

        self.domain_id = domain_id
        self.lang_id = lang_id
        self.message_id = message_id

    def __str__(self):
        return "%s: %s: %s updated" % (
            self.domain_id, self.lang_id, self.message_id)
