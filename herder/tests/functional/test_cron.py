# -*- coding: utf-8 -*-
import herder.tests
from minimock import Mock
from herder.tests import *
import herder.tests.functional.test_account
from herder.tests.functional.test_language import TestLanguageController
from herder.tests.functional.test_account import TestProfilePrefLangSpecificMail
import herder.events.cron.cli
import smtplib
from herder.tests.functional.test_language import TestLanguageController
import herder.controllers.language

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
        >>> lc = herder.controllers.language.LanguageController()
        >>> 
        '''
