import os
from babel.messages import catalog

from pylons import config

import domain
import message

class TransactionAbort(Exception):
    pass

class Language(object):
    """A specific language within a domain."""

    # Suggestion storage:
    ## for string called yourmom.txt, store in yourmom/ with
    ## filename as user ID of user 
    def suggest(self, username, i18n_key, new_value):
        # Same locking story as self.update
        cur_msg = self[i18n_key]
        cur_msg.suggest(username, new_value)

        final_value = cur_msg.get_suggestion(username)
        if final_value != new_value:
            raise TransactionAbort("Goign too fast...?")
        return True

    def update(self, i18n_key, old_value, new_value):
        # NOTE: I don't know how to lock the model, so we'll just try
        # our changes, and assert they stuck at the end of this.
        # FIXME: That is still racey because someone could:
        ## * We could correctly update i18n_key to new_value
        ## * Another thread could change i18n_key to some_other_value
        ## * We would check the value and think the transaction went wrong
        # But it's only racey in a causes-false-negatives way.
        current_value = self[i18n_key]
        if current_value.string != old_value:
            raise TransactionAbort("The old value (%s) we were passed did not match up with the current value (%s) for key (%s)" % (old_value, current_value.string, i18n_key))
        # Otherwise, it's safe.
        current_value.update(new_value=new_value, old_value=old_value)

        # Check that the update stuck (and e.g. that no one beat us to the race)
        final_value = self[i18n_key]
        if final_value.string != new_value:
            raise TransactionAbort("The new value did not save properly. Perhaps someone beat us in a race of updating the file.")
        # FIXME: Unlock the model

    @classmethod
    def by_domain_id(cls, domain_id, lang):

        return domain.Domain.by_name(domain_id).get_language(lang)

    def __init__(self, domain, lang):
        self.domain = domain
        self.lang = lang

    def __str__(self):
        return self.lang

    def __cmp__(self, other):
        if isinstance(other, Language):
            return cmp(str(self), str(other))

        return cmp(self, other)

    @property
    def name(self):
        return str(self)

    @property
    def _message_store(self):

        return os.path.join(self.domain.path, self.lang)

    def __contains__(self, key):
        """Return True if this language contains a message with the
        given key."""

        if isinstance(key, message.Message):
            key = key.id

        return os.path.exists(message.message_datafile_path(self, key))

    def __getitem__(self, key):
        """Convenience method for accessing a Message by id."""

        if key in self:
            return message.Message(self, key)

        raise KeyError

    def __delitem__(self, key):
        """Remove a Message from the language."""

        if key in self:
            os.remove(message.message_datafile_path(self, key))

        else:
            raise KeyError

    def __len__(self):
        
        return len(
            [f for f in os.listdir(self._message_store)
             if f[-4:] == '.txt']
            )

    def __iter__(self):

        for filename in os.listdir(self._message_store):

            if filename[-4:] != '.txt':
                continue

            yield (message.Message(self, filename[:-4]))

    def get_catalog(self):
        """Return the Language as a Babel Catalog object."""

        result = catalog.Catalog(domain=self.domain.name,
                                 locale=self.lang,
                                 fuzzy=False)

        # for each Herder Message in this language
        for h_msg in self:
            
            # add a Babel Message to the result
            result[h_msg.id] = catalog.Message(h_msg.id,
                                               string=h_msg.string)

        return result
