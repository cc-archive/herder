import logging
import smtplib
import herder.model

import PyRSS2Gen
import datetime
import feedparser
from pylons import config
import zope.component
from herder.events.events import HerderEvent
import os.path

@zope.component.adapter(HerderEvent)
def feed_handler(event):
    dest_dir = os.path.join(config.get('herder.feed_dir'), event.domain_id, event.lang_id)
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir, mode=0755)
    dest_file = os.path.join(dest_dir, 'index.xml')

    # Create an item for right now
    items = [
        PyRSS2Gen.RSSItem(
            title="Someone updated string %s" % event.message_id,
            pubDate = datetime.datetime.now())]

    # Take the existing file, and pull out the past into previous_entries
    if os.path.exists(dest_file):
        parsed = feedparser.parse(open(dest_file))
        for entry in parsed.entries:
            entry_as_item = PyRSS2Gen.RSSItem(
                title=entry.title,
                pubDate = datetime.datetime(
                    *entry.updated_parsed[:7]))
            items.append(entry_as_item)

    # Set up our usual header
    rss = PyRSS2Gen.RSS2(
        title='Translation tool feed for language %s in domain %s' % \
            (event.lang_id, event.domain_id),
        link = 'http://example.com/', # FIXME
        description  = "Just what the title says",
        # No GUID...
        pubDate = datetime.datetime.now(),
        items=items)

    # Jam it onto disk.
    # FIXME: Use some trivial AtomicFile class that you put on PyPI.
    fd = open(dest_file + '.tmp', 'w')
    rss.write_xml(fd)
    fd.close()
    os.rename(dest_file + '.tmp', dest_file)

@zope.component.adapter(HerderEvent)
def logging_handler(event):
    # omg unicode bbq
    import sys
    import codecs
    unicode_out = codecs.getwriter('utf-8')(sys.stdout)
    unicode_out.write(unicode(event) + '\n')

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
        zope.component.provideHandler(feed_handler)
