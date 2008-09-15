# -*- coding: utf-8 -*-
import herder.tests
from minimock import Mock
from herder.tests import *
import herder.tests.functional.test_account
from herder.tests.functional.test_language import TestLanguageController

class TestMail(TestController):
    def test_your_mom(self):
        '''
        >>> 'your mom'
        'your mom'
        '''

    def test_no_mail_gets_set_for_most_edits(self):
        r'''
        >>> tlc = TestLanguageController()
        >>> import smtplib
        >>> smtplib.SMTP = Mock('smtplib.SMTP', returns = Mock('smtp_connection'))
        >>> tlc.test_edit_string_as_bureau()
        cc_org: en_US: country.us updated
        cc_org: en_US: country.us updated
        >>>
        '''

    # Following test is brittle; it should assert things about the message,
    # not its literal format. )-:
    def test_email_sending(self):
#        r'''
#        >>> tlc = TestLanguageController()
#        >>> import smtplib
#        >>> smtplib.SMTP = Mock('smtplib.SMTP', returns = Mock('smtp_connection'))
#        >>> tlc.test_edit_string_as_bureau()
#        cc_org: en_US: country.us updated by user ID 1 <bureau@example.com>
#        Called smtplib.SMTP('localhost')
#        Called smtp_connection.sendmail(
#            'herder-bounces@localhost',
#            [u'bureau@example.com'],
#            u'To: bureau@example.com\nFrom: herder-bounces@localhost\nSubject: Message update for country.us\n\nJust so you know, user ID 1 changed country.us.')
#        Called smtp_connection.quit()
#        cc_org: en_US: country.us updated by user ID 1 <bureau@example.com>
#        Called smtplib.SMTP('localhost')
#        Called smtp_connection.sendmail(
#            'herder-bounces@localhost',
#            [u'bureau@example.com'],
#            u'To: bureau@example.com\nFrom: herder-bounces@localhost\nSubject: Message update for country.us\n\nJust so you know, user ID 1 changed country.us.')
#        Called smtp_connection.quit()
#        
#        >>> 
#        '''
        pass

