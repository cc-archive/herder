import logging
import smtplib
import herder.model

import zope.component
from herder.events.events import HerderEvent

@zope.component.adapter(HerderEvent)
def logging_handler(event):
    print event

@zope.component.adapter(HerderEvent)
def email_handler(event):
    prefs_who_care = herder.model.meta.Session.query(
        herder.model.pref.Pref).filter_by(
        pref_name='email_notify', pref_value=True, lang_id=event.lang_id)

    email_these_dudes = set()
    for pref in prefs_who_care:
        if herder.model.meta.Session.query(
            herder.model.pref.Pref).filter_by(
            pref_name='email_enabled', pref_value=True, lang_id='*',
            domain_id='*', user_id=pref.user_id):
            email_these_dudes.update(
                herder.model.meta.Session.query(
                    herder.model.user.User).filter_by(
                    user_id=pref.user_id))

    if email_these_dudes:
        server = smtplib.SMTP('localhost') # hard-code this
        # FIXME: should use MIME or something to generate the email
        server.sendmail('herder-bounces@localhost',
                        [dude.email for dude in email_these_dudes],
                        '\n'.join(
                ('From: herder-bounces@localhost',
                 'Subject: Message update for %s' % event.message_id,
                 '',
                 'Just so you know, the message %s changed in the language %s.' % (event.message_id, event.lang_id))))
        server.quit()

# beenhere works around an issue with nosetest + Pylons,
# where the registration gets called once per test run it seems.
# See: http://code.creativecommons.org/issues/issue31

# fine, so only let it be run once.
beenhere = False
def register():
    """Register included event handlers."""
    global beenhere
    if not beenhere:
        beenhere = True
        # register basic logging handler
        zope.component.provideHandler(logging_handler)
        zope.component.provideHandler(email_handler)
