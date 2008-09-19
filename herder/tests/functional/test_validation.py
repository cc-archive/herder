# -*- coding: utf-8 -*-
import herder.tests
from herder.tests import *
from herder.tests.functional.test_language import TestLanguageController
from herder.tests.functional.test_account import TestProfilePrefLangSpecificMail

class TestValidation(TestController):
    def test_invalid_change_does_not_save(self):
        r'''
        >>> tlc = TestLanguageController()
        >>> tlc.test_edit_string_as_bureau(new_value='X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*', should_fail=True)
        >>> 
        '''

