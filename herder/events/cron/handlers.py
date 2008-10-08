import zope.component
from herder.events.send_email import send_email
from herder.events.cron.events import HerderMonthlyEvent
import collections

@zope.component.adapter(HerderMonthlyEvent)
def monthly_status_reminders(event):
    '''For all domains, for every language, email (for now) the
    currently-pending suggestions to the translation's maintainer.'''
    import herder.model

    print 'Emailing out monthly status reminders...'
    domain_id = '*'
    # Take a look at all the translators
    translator_role = herder.model.meta.Session.query(
        herder.model.role.Role).filter_by(
        role_name='translator').one()

    all_translator_auths = herder.model.meta.Session.query(
        herder.model.authorization.Authorization).filter_by(
        role_id=translator_role.role_id)

    # Figure out who cares about what
    user_id2domain2language = collections.defaultdict(
        lambda: collections.defaultdict(set))

    # For each such authorization, add a note to user_id2email
    # with the message to be sent out as respects that authorization
    for auth in all_translator_auths:

        # domain_id is * and this is here this whole app ignores
        # domain_id as far as permissions.  I have this assertion to
        # mark that if we start caring about domain_id this code will
        # need to be re-visited.  Keep in mind we *do* check lang_id.
        assert auth.domain_id == domain_id

        # Check for relevant pending suggestions
        import fnmatch
        mydomains = [d for d in herder.model.domain.Domain.all()
                     if fnmatch.fnmatch(d.name, auth.domain_id)]

        for mydomain in mydomains:
            # Check what languages he cares about
            mylangs = [l for l in mydomain.languages
                       if fnmatch.fnmatch(l.name, auth.lang_id)]
            for mylang in mylangs: 
                user_id2domain2language[auth.user_id][mydomain].add(mylang)

    # So now we know the mapping from user_id to domain to language in
    # that domain

    for user_id in user_id2domain2language:
        growing_message = []
        for domain in user_id2domain2language[user_id]:
            # For each language, get all the suggestions
            for lang_id in user_id2domain2language[user_id][domain]:
                lang_obj = herder.model.language.Language.by_domain_id(
                    unicode(domain), unicode(lang_id))
                suggestions = lang_obj.get_all_suggestions()
                if not suggestions:
                    continue
                growing_message.append(
                    u'''The language %s that you can translate has
pending suggestions for these strings:

%s''' % (
                        lang_id, ', '.join(sorted(set(
                                    suggestions.keys())))))

        # Great, now email that to user_id
        if not growing_message:
            continue
        body = u'\n\n'.join(growing_message)
        recipient_addrs = [unicode(
            herder.model.meta.Session.query(
            herder.model.user.User).filter_by(
            user_id=user_id).one().email).encode('ascii')]
        send_email(
            '"Herder Monthly Update" <herder@localhost>',
            recipient_addrs,
            u'Monthly update: Suggestions available for your language',
            body)
    print '...success.'

# beenhere works around an issue with nosetest + Pylons,
# where the registration gets called once per test run it seems.
# See: http://code.creativecommons.org/issues/issue31

# fine, so only let it be run once.
def register(beenhere = []):
    """Register included event handlers."""
    if not beenhere:
        beenhere.append(beenhere) # hah
        # register montly status reminder
        zope.component.provideHandler(monthly_status_reminders)
