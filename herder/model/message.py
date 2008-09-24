import os
import exceptions
import string
import codecs

from pylons import config

import domain
import language

from herder import events
from errors import *

def message_datafile_path(language, id):
    """Return the datafile path for locating a particular message in the
    language."""

    return os.path.join(language.domain.path, language.name,
                        id + '.txt')

class Message(object):
    """A specific string in a particular language."""

    ID_PATH_CHARS = string.ascii_letters + '. '

    @classmethod
    def by_domain_language_id(cls, domain_id, language_id, message_id):
        """Return the Message for a particular domain and language."""

        return Message(language.Language.by_domain_id(domain_id, language_id),
                       message_id)

    def __init__(self, language, id):
        
        self.language = language
        self.id = self.normalize_id(id)

    def normalize_id(self, id):
        """Return the normalized version of the string ID."""

        return id.lower()

        # calculate the filename
        id_src = "".join([n for n in id if n in self.ID_PATH_CHARS]).lower()
        words = id_src.split()

        if len(words) == 1:
            return words[0] 

        return "-".join([''] + words[:4] + [str(abs(hash(id)))])

    @property
    def datafile_path(self):
        """Return the file path used to store this message."""

        return message_datafile_path(self.language, self.id)

    @property
    def string(self):
        """Return the current value of the string."""
    
        if not os.path.exists(self.datafile_path):
            return ""

        return codecs.open(self.datafile_path, 'r', 'utf-8').read()

    def update(self, new_value, old_value=None):
        """Update a string; if old_value is provided, only perform the edit
        if the value has not been editted in the interim."""

        assert type(new_value) == unicode
        if old_value is not None:
            if self.string != old_value:
                raise TransactionAbort(
                    "Old value and new value aren't the same!")

        # Make an event and see what the validators think of it
        event = events.MessageUpdateEvent.with_message(
            self, old_value=old_value, new_value=new_value)

        validation_problems = []
        
        if validation_problems:
            raise TransactionError('\n'.join(validation_problems))

        # Otherwise, we're great!
        codecs.open(self.datafile_path, mode='w', 
                    encoding='utf-8').write(new_value)

        events.handle(event)

    def sugg_path(self, user_id = None):
        sugg_path = os.path.join(self.language.domain.path, self.language.name,
                                 self.id + '.sugg.d')
        if user_id is not None:
            assert(type(user_id) == int)
            user_str = str(user_id)
            sugg_path = os.path.join(sugg_path, user_str + '.txt')

        return sugg_path

    def suggest(self, user_id, suggestion):
        """Store a suggestion for the string we are."""

        # figure out where to store this suggestion
        if not os.path.exists(self.sugg_path()):
            os.makedirs(self.sugg_path())

        # write the suggestion to disk
        fd = codecs.open(self.sugg_path(user_id), 'w', encoding='utf-8')
        assert type(suggestion) == unicode
        fd.write(suggestion)
        fd.close()

    def del_suggestion(self, user_id, fail_if_empty = False):
        try:
            os.unlink(self.sugg_path(user_id))
            return None
        except IOError, e:
            if e.errno == 2: # No such file or directory
                if fail_if_empty:
                    raise
                else:
                    return None
            # All other errors get raised as usual, because wtf
            raise

    def get_suggestion(self, user_id, fail_if_empty = False):
        '''Return just the single lousy Unicode string that this user suggested, or None.'''
        try:
            fd = codecs.open(self.sugg_path(user_id), encoding='utf-8')
        except IOError, e:
            if e.errno == 2: # No such file or directory
                if fail_if_empty:
                    raise
                else:
                    return None
            # All other errors get raised as usual, because wtf
            raise
        return fd.read()

    def get_suggestions(self):
        # Racey.  Hmm, maybe this filesystem DB thing does suck.
        ret = {}
        try:
            sugg_dir_contents = os.listdir(self.sugg_path())
        except exceptions.OSError, e:
            if e.errno == 2: # No such file or directory
                sugg_dir_contents = ()
            else:
                raise
        for sugg_filename in sugg_dir_contents:
            user_id = int(sugg_filename.split('.')[0])
            suggestion = self.get_suggestion(user_id)
            if suggestion:
                ret[user_id] = suggestion

        return ret

