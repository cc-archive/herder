# -*- coding: utf-8 -*-
import herder.tests
from herder.tests import *
from herder.tests.functional.test_language import TestLanguageController
from herder.tests.functional.test_account import TestProfilePrefLangSpecificMail

class TestValidation(TestController):
    def test_invalid_change_does_not_save(self):
        r'''
        >>> tlc = TestLanguageController()
        >>> tlc.test_edit_string_as_bureau(new_value='X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*', should_fail=True, error_string='ZOMG INFEKTED')
        >>>
        '''
    def test_invalid_change_does_not_save(self):
        r'''
        >>> tlc = TestLanguageController()
        >>> tlc.test_edit_string_as_bureau(new_value='Some random ${template}', should_fail=True, error_string='has these spurious template string(s)')
        >>>
        '''

class TestValidationTwo(TestController):

    def test_invalid_change_does_not_save_requires_right_message(self):
        tlc = TestLanguageController()
        try:
            tlc.test_edit_string_as_bureau(new_value='X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*', should_fail=True, error_string='wrong message')
        except AssertionError:
            # great, it was supposed to fail.
            return
        assert False, "It should have failed."



