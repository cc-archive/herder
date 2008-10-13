# -*- coding: utf-8 -*-
import herder.tests
from minimock import Mock
from herder.tests import *
from herder.tests.functional.test_language import TestLanguageController
from herder.tests.functional.test_account import do_register
import herder.events.cron.cli
import smtplib
from herder.tests.functional.test_language import TestLanguageController

class TestCron(TestController):
    def test_monthly_email_sans_suggestions(self):
        r'''
        >>> smtplib.SMTP = Mock('smtplib.SMTP', returns = Mock('smtp_connection'))
        >>> herder.events.cron.cli.cron(['-c', 'test.ini', '-m'])
        Emailing out monthly status reminders...
        ...success.
        >>>
        '''

    def test_monthly_email_with_suggestions(self):
        r'''
        >>> smtplib.SMTP = Mock('smtplib.SMTP', returns = Mock('smtp_connection'))
        >>>
        # Log in as some new user
        >>> u, p, e, n = [herder.model.user.random_alphanum() for k in range(4)]
        >>> tlc = TestLanguageController()
        >>> do_register(tlc.app, user_name=u, password=p, human_name=n, email=e + '@example') #doctest: +ELLIPSIS
        '...'
        >>> tlc.login_as(u, p) #doctest: +ELLIPSIS
        <Response 200 ...>
        >>> tlc.test_make_suggestion_as_non_bureau(already_logged_in_as=u, do_suggest=True, do_delete=False)
        >>> herder.events.cron.cli.cron(['-c', 'test.ini', '-m']) #doctest: +ELLIPSIS
        Emailing out monthly status reminders...
        Called smtplib.SMTP('localhost')
        Called smtp_connection.sendmail(
            'herder-bounces@localhost',
            ['bureau@example.com'],
            '...pending suggestions...country.us')
        Called smtp_connection.quit()
        ...success.
        >>> tlc.test_make_suggestion_as_non_bureau(already_logged_in_as=u, do_suggest=False, do_delete=True)
        '''
