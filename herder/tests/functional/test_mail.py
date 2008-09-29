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
        cc_org: en_US: country.us updated from <United States> to <¿Untied States?> by 1
        cc_org: en_US: country.us updated from <¿Untied States?> to <United States> by 1
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
	>>> import base64
	>>> base64.b64encode('¿Untied States?')
	'wr9VbnRpZWQgU3RhdGVzPw=='
	>>> base64.b64encode('United States')
	'VW5pdGVkIFN0YXRlcw=='
        >>> tpm = TestProfilePrefLangSpecificMail()
        >>> tpm.test_profile_pref_language_specific_mail(do_unset=False)
        >>> tlc = TestLanguageController()
        >>> import smtplib
        >>> smtplib.SMTP = Mock('smtplib.SMTP', returns = Mock('smtp_connection'))
        >>> tlc.test_edit_string_as_bureau() #doctest: +ELLIPSIS
        cc_org: en_US: country.us updated from <United States> to <¿Untied States?> by 1
        Called smtplib.SMTP('localhost')
        Called smtp_connection.sendmail(
            'herder-bounces@localhost',
            ['bureau@example.com'],
            '...Subject: Message update for country.us in en_US...United States...Untied States...')
        Called smtp_connection.quit()
        cc_org: en_US: country.us updated from <¿Untied States?> to <United States> by 1
        Called smtplib.SMTP('localhost')
        Called smtp_connection.sendmail(
            'herder-bounces@localhost',
            ['bureau@example.com'],
            '...Subject: Message update for country.us in en_US...Untied States...United States...')
        Called smtp_connection.quit()
        >>> tpm.test_profile_pref_language_specific_mail(do_set=False)
        >>>
        >>> tlc.test_edit_string_as_bureau()
        cc_org: en_US: country.us updated from <United States> to <¿Untied States?> by 1
        cc_org: en_US: country.us updated from <¿Untied States?> to <United States> by 1
        >>>
        '''
        pass

