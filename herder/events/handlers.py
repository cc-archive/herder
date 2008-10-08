'''Store event handlers.'''

import PyRSS2Gen
import datetime
import feedparser
from pylons import config
import zope.component
from herder.events.events import MessageUpdateEvent
from herder.events.send_email import send_email
import os.path

import git
import random
import time

@zope.component.adapter(MessageUpdateEvent)
def feed_handler(event):
    import herder.model
    '''Generate an RSS feed (pretty lamely, currently) using the event.'''
    dest_dir = os.path.join(config.get('herder.feed_dir'), event.domain_id,
                            event.lang_id)
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir, mode=0755)
    dest_file = os.path.join(dest_dir, 'index.xml')

    # Create an item for right now
    items = [
        PyRSS2Gen.RSSItem(
            title=u"Someone updated string %s" % event.message_id,
            description=event.long_flowy_message(joiner='<p>'),
            pubDate = datetime.datetime.now())]

    # Take the existing file, and pull out the past into previous_entries
    if os.path.exists(dest_file):
        parsed = feedparser.parse(open(dest_file))
        for entry in parsed.entries:
            entry_as_item = PyRSS2Gen.RSSItem(
                title=entry.title,
                description=entry.get('summary', ''),
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

class Locker:
    def __init__(self, lock_path, timeout=5):
        self.lock_dir = os.path.join(lock_path, '.locked')
        self.slept = 0
        self.timeout = timeout
    def _lock(self):
        os.mkdir(self.lock_dir)
    def lock(self):
        success = False
        while not success:
            try:
                self._lock()
                success = True
            except OSError, e:
                if e.errno == 17: # File exists
                    will_sleep = (0.1 * random.random())
                    self.slept += will_sleep
                    if self.slept > self.timeout:
                        raise
                    time.sleep(will_sleep)
                else:
                    raise # yeah, what the heck error did we get?
        return success
    def unlock(self):
        os.rmdir(self.lock_dir)

def plus_txt(u):
    return u.encode('utf-8') + '.txt'

@zope.component.adapter(MessageUpdateEvent)
def git_commit_handler(event):
    import herder.model
    # If no one cares, get out.
    someone_cares = config.get('herder.do_git_commits', '')
    if someone_cares != 'true':
        return

    # Grab the right path...
    repo_dir = os.path.join(config.get('herder.po_dir'), event.domain_id)
    # lock it...
    lock = Locker(repo_dir)
    lock.lock()
    # ...and now do our git operations
    repo = git.Repository(repo_dir)
    
    # Grab the latest commit on master
    commit = repo.heads['refs/heads/master'].commit
    commitname = commit.name
    
    # FWIW, an event should only be able to change an already-existing path
    new_blob = git.Blob(repo)
    new_blob.contents = event.new_value.encode('utf-8')
    
    # We're always looking in the subdir that is our lang_id
    subtree = commit.tree[event.lang_id.encode('utf-8')]
    
    # make sure the old blob looks like the old value,
    assert (subtree[plus_txt(event.message_id)
                    ].contents == event.old_value.encode('utf-8'))
    # and squeeze in the new value:
    subtree[plus_txt(event.message_id)] = new_blob
    commit.tree[event.lang_id.encode('utf-8')] = subtree
    
    user_obj = herder.model.meta.Session.query(
        herder.model.user.User).filter_by(user_id=event.user_id).one()
    commit.author = git.commit.Person(user_obj.user_name.encode('utf-8'),
                                      user_obj.email.encode('utf-8'))

    assert not commit.name
    commit.commit(message=unicode(event).encode('utf-8'))
    assert commit.name

    # Committed, but need to update the ref!
    ref = git.Ref(repo, 'refs/heads/master')
    ref.update(commit)
    
    # and unlock
    lock.unlock()

@zope.component.adapter(MessageUpdateEvent)
def logging_handler(event):
    # omg unicode bbq
    import sys
    import codecs
    unicode_out = codecs.getwriter('utf-8')(sys.stdout)
    unicode_out.write(unicode(event) + '\n')

@zope.component.adapter(MessageUpdateEvent)
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
        body = event.long_flowy_message()
        msg_from = '"Translation System" <herder-bounces@localhost>'

        recipient_addrs = [unicode(dude.email).encode('ascii') for dude in
                  email_these_dudes]

        send_email(msg_from, recipient_addrs, subject, body)

# beenhere works around an issue with nosetest + Pylons,
# where the registration gets called once per test run it seems.
# See: http://code.creativecommons.org/issues/issue31

# fine, so only let it be run once.
def register(beenhere = []):
    """Register included event handlers."""
    if not beenhere:
        beenhere.append(beenhere) # hah
        # register basic logging handler
        zope.component.provideHandler(logging_handler)
        zope.component.provideHandler(git_commit_handler)
        zope.component.provideHandler(email_handler)
        zope.component.provideHandler(feed_handler)
