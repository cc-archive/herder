# -*- coding: utf-8 -*-
import herder.tests
from pylons import config
import os.path
from herder.tests import *
from herder.tests.functional.test_language import TestLanguageController
import datetime
import feedparser

class TestFeed(TestController):
    # Note: Architecture of RSS feeds is currently very lame,
    # for now printing just that the RSS feed noticed an event,
    # since without versioning there's no way to be sure of what 
    # actually changed.

    # Later we should pass around version control system IDs in
    # the event, or the whole event's data and metadata.
    def test_make_event_and_watch_rss_feed_update_properly(self):
        # check the date and calc. the filename
        with_nanosec = datetime.datetime.now()
        now = datetime.datetime(*with_nanosec.timetuple()[:7])
        filename = os.path.join(
            config['herder.feed_dir'], 'cc_org', 'en_US', 'index.xml')

        # clear it if it's there
        if os.path.exists(filename):
            os.unlink(filename)

        # edit and un-edit a string
        tlc = TestLanguageController()
        tlc.test_edit_string_as_bureau()

        # Now we parse the feed to show it got updated twice
        parsed = feedparser.parse(open(filename))
        assert len(parsed.entries) == 2
        relevant = [ entry for entry in parsed.entries if
                     datetime.datetime(*entry.updated_parsed[:7]) >=
                     now ]
        assert len(relevant) == 2
        for entry in relevant:
            assert 'Untied States' in entry.summary


        

