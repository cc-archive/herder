'''Store event handlers.'''

import smtplib

import PyRSS2Gen
import datetime
import feedparser
from pylons import config
import zope.component
from herder.events.events import HerderEvent
import os.path

from email.MIMEText import MIMEText
from email.Header import Header
import email.encoders
from email.Utils import parseaddr, formataddr

@zope.component.adapter(HerderEvent)
def feed_handler(event):
    '''Generate an RSS feed (pretty lamely, currently) using the event.'''
    dest_dir = os.path.join(config.get('herder.feed_dir'), event.domain_id,
			    event.lang_id)
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
    out_fd = open(dest_file + '.tmp', 'w')
    rss.write_xml(out_fd)
    out_fd.close()
    os.rename(dest_file + '.tmp', dest_file)

@zope.component.adapter(HerderEvent)
def logging_handler(event):
    # omg unicode bbq
    import sys
    import codecs
    unicode_out = codecs.getwriter('utf-8')(sys.stdout)
    unicode_out.write(unicode(event) + '\n')

@zope.component.adapter(HerderEvent)
def email_handler(event, header_charset='utf-8', body_charset='utf-8'):
    import herder.model
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
	# First, make our nice Unicoded subject and body
        subject = u'Message update for %s in %s' % (event.message_id,
                                                    event.lang_id)
        body = u'\n'.join([
                u'The language %s changed for its translation of %s' % (
                    event.lang_id, event.message_id),
                u''
                u'It used to be:'
                u'',
                event.old_value,
                u'',
                u'But now it is:'
                u'',
                event.new_value,
                u''
                u'Lovingly,'
                u'',
                u'The Translation Tool.'])

	# Python Unicode sanity c/o http://mg.pov.lt/blog/unicode-emails-in-python.html

	# Prepare SMTP-level sender and recipient
        sender_name, sender_addr = parseaddr(
            '"Translation System" <herder-bounces@localhost>')

        # We must always pass Unicode strings to Header, otherwise it will
        # use RF C2047 encoding even on plain ASCII strings.
        sender_name = str(Header(unicode(sender_name), header_charset))
        # no recipient_name in the header

        # Make sure email addresses do not contain non-ASCII
        # characters
        # (FIXME: This could blow up at runtime if we don't
        # assert this at other layers, like the DB!)
        sender_addr = unicode(sender_addr).encode('ASCII')
        recipient_addrs = [unicode(dude.email).encode('ascii') for dude in
                           email_these_dudes]

	# Create the message ('plain' stands for Content-Type: text/plain)
        msg = MIMEText(body.encode(body_charset), 'plain', body_charset)
	# FIXME: I want quoted-printable, gosh darn it
        msg['From'] = formataddr( (sender_name, sender_addr) )
        # Leave "To:" blank
        msg['Subject'] = Header(unicode(subject), header_charset)

        server = smtplib.SMTP('localhost') # hard-coded
        server.sendmail(sender_addr, recipient_addrs, msg.as_string())
        server.quit()

# beenhere works around an issue with nosetest + Pylons,
# where the registration gets called once per test run it seems.
# See: http://code.creativecommons.org/issues/issue31

# fine, so only let it be run once.
def register(beenhere = []):
    """Register included event handlers."""
    if not beenhere:
        beenhere.append(True)
        # register basic logging handler
        zope.component.provideHandler(logging_handler)
        zope.component.provideHandler(email_handler)
        zope.component.provideHandler(feed_handler)
