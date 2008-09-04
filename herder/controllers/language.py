import urllib
import logging
import collections

import jsonlib
from pylons.decorators import jsonify

from herder.lib.base import *
import herder.model

log = logging.getLogger(__name__)
import xml.sax.saxutils

class LanguageController(BaseController):
    requires_auth = ('edit_string',)

    def view(self, domain, id):
        """View a specific domain language."""

        c.domain = herder.model.Domain.by_name(domain)
        c.language = c.domain.get_language(id)

        return render('/language/view.html')

    def admin(self, domain, id):
        """Administer a language in a domain."""

        # get the Domain and Language objects and render the template
        c.domain = herder.model.Domain.by_name(domain)
        c.language = c.domain.get_language(id)

        return render('/language/admin.html')
    
    def _editor(self, domain, id, template_fn):
        """Abstraction of the editor view."""

        c.domain = herder.model.Domain.by_name(domain)
        c.language = c.domain.get_language(id)

        c.addl_langs = request.params.getall('lang')
        c.addl_langs_list = ",".join(['"%s"' % n for n in c.addl_langs])
        c.addl_langs_qs = urllib.urlencode([('lang', n) for n in c.addl_langs])

        return render(template_fn)

    def all(self, domain, id):

        return self._editor(domain, id, '/language/all.html')

    def untranslated(self, domain, id):

        return self._editor(domain, id, '/language/untranslated.html')

    def suggestions(self, domain, id):

        return self._editor(domain, id, '/language/suggestions.html')

    @jsonify
    def suggestions_for_message(self, domain, id, message_id):
        domain = herder.model.Domain.by_name(domain)
        language = domain.get_language(id)
        message = language[message_id]
        suggestions = message.get_suggestions()
        ret = []
        for username in suggestions:
            me = {}
            me['author'] = username
            me['suggestion'] = suggestions[username]
            ret.append(me)
        return {'result': ret}

    def lame_suggestions_ui(self, domain, id):
        c.domain = herder.model.Domain.by_name(domain)
        c.language = c.domain.get_language(id)

        message2user2suggestion = collections.defaultdict(dict)
        # Figure out what users have suggestions for which strings
        for message in c.language:
            user2suggestion = message.get_suggestions()
            if user2suggestion:
                message2user2suggestion[message] = user2suggestion

        return render('/language/lame_suggestions_ui.html',
            data=message2user2suggestion)

    def _messages(self, domain, id, filter=lambda x:True):
        domain = herder.model.Domain.by_name(domain)
        langs = {id:domain.get_language(id)}
    
        for l_id in request.params.getall('lang'):
            langs[l_id] = domain.get_language(l_id)
            
        result = dict(domain=domain.name,
                      language=id,
                      strings=[])

        for s in langs[id]:
            if filter(s):
                string_record = dict(id=s.id, value=s.string)

                for l in langs:
                    string_record[l] = langs[l][s.id].string

                result['strings'].append(string_record)

        return result

    @jsonify
    def strings(self, domain, id):
        return self._messages(domain, id, lambda s:bool(s.id))

    @jsonify
    def untranslated_strings(self, domain, id):

        en = herder.model.DomainLanguage.by_domain_id(domain, 'en')

        def untrans_filter(message):
            return (message.id and ( not(message.string) or 
                                     message.string == en[message.id].string)
                    )

        return self._messages(domain, id, untrans_filter)

    @jsonify
    def suggestion_avail_strings(self, domain, id):

        en = herder.model.DomainLanguage.by_domain_id(domain, 'en')

        def suggestion_avail_filter(message):
            return bool(message.get_suggestions())

        return self._messages(domain, id, suggestion_avail_filter)

    def suggestion_action_unknown(self, domain, id):
        return render('/language/suggestion_action_unknown.html')

    def suggestion_action(self, domain, id):
        if not 'delete' in request.params:
            redirect_to(action='suggestion_action_unknown')
        # It's safe to assume deleting is what's meant.
        user_id = int(request.params['user_id'])
        message_id = xml.sax.saxutils.unescape(request.params['message_id'])
        domain = herder.model.DomainLanguage.by_domain_id(domain, id)
        domain[message_id].del_suggestion(user_id)
        redirect_to('lame_suggestions_ui', domain, id, message='Successfully deleted one suggestion.')

    def edit_string(self, domain, id):
        """Edit an individual string."""

        language = herder.model.DomainLanguage.by_domain_id(domain, id)
        
        data = jsonlib.read(request.params['data'])

        # XXX trap an exception here that would be raised if edit conflict
        if 'translate' in self._get_roles(request.environ, domain, id):
            # store the translation
            language.update(data['id'], data['old_value'], data['new_value'])
        else:
            # store the translation as a suggestion
            language.suggest(session['user'].user_id,
                             data['id'], data['new_value'])



