# -*- coding: utf-8 -*-
import herder.tests
from minimock import Mock
from herder.tests import *
import herder.tests.functional.test_account
from herder.tests.functional.test_language import TestLanguageController
from herder.tests.functional.test_account import TestProfilePrefLangSpecificMail

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

    # But the test makes sense:
    # Subscribe the bureau user to en_US updates, and edit an en_US string
    # make sure an email gets sent.

    # Unset his desire for updates, and then make sure it does not when
    # we do another edit.
    def test_email_sending(self):
        r'''
        >>> tpm = TestProfilePrefLangSpecificMail()
        >>> tpm.test_profile_pref_language_specific_mail(do_unset=False)
        >>> tlc = TestLanguageController()
        >>> import smtplib
        >>> smtplib.SMTP = Mock('smtplib.SMTP', returns = Mock('smtp_connection'))
        >>> tlc.test_edit_string_as_bureau()
        cc_org: en_US: country.us updated
        Called smtplib.SMTP('localhost')
        Called smtp_connection.sendmail(
            'herder-bounces@localhost',
            [u'bureau@example.com'],
            u'From: herder-bounces@localhost\nSubject: Message update for country.us\n\nJust so you know, the message country.us changed in the language en_US.')
        Called smtp_connection.quit()
        cc_org: en_US: country.us updated
        Called smtplib.SMTP('localhost')
        Called smtp_connection.sendmail(
            'herder-bounces@localhost',
            [u'bureau@example.com'],
            u'From: herder-bounces@localhost\nSubject: Message update for country.us\n\nJust so you know, the message country.us changed in the language en_US.')
        Called smtp_connection.quit()
        >>> tpm.test_profile_pref_language_specific_mail(do_set=False)
        >>>
        >>> tlc.test_edit_string_as_bureau()
        cc_org: en_US: country.us updated
        cc_org: en_US: country.us updated
        >>>
        '''
        pass

