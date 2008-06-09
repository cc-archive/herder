# -*- coding: utf-8 -*-
from herder.tests import *
import herder.tests.functional.test_account
import herder.model.user
import jsonlib
import BeautifulSoup

class TestLanguageController(TestController):

    def test_view(self):
        response = self.app.get(url_for(controller='language', action='view',
            domain='cc_org', id='en'))
        return True # FIXME: Test something here someday
    def test_strings_contain(self, desired_key = 'country.us', desired_value='United States'):
        response = self.app.get(url_for(controller='language', action='strings',
            domain='cc_org', id='en'))
        value = jsonlib.read(response.body)
        strings = value['strings']
        found_what_we_like = False
        for stringthing in strings:
            if stringthing['id'] == desired_key:
                assert stringthing['value'] == desired_value
                found_what_we_like = True
                break
        assert found_what_we_like
       
    def test_edit_string_as_admin(self):
        # Pretend to be admin
        self.login_as('admin', admin_password)

        # First, change it so old -> new
        i18n_key = 'country.us'
        old = 'United States'
        new = u'¿Untied States?'
        self.test_strings_contain(desired_key=i18n_key, desired_value=old)

        url_indeed = url_for(controller='language', action='edit_string',
            domain='cc_org', id='en_US')
        response = self.app.post(url_indeed, 
            params={'data': 
            jsonlib.write({'id': i18n_key,
                'new_value': new, 'old_value': old})})
        # Check that the write took with a deep test
        import herder.model.language 
        lang = herder.model.language.Language.by_domain_id(domain_id='cc_org',
                                                           lang='en_US')
        assert lang[i18n_key].string == new
       
        # Check that the write took with a UI-level test
        
        # FIXME: Don't disable this check.
        # self.test_strings_contain(desired_key=i18n_key, desired_value=new)
        # Good, the new value stuck.

        # Then, change it back (just because I feel bad)
        response = self.app.post(url_indeed, 
            params={'data': 
            jsonlib.write({'id': i18n_key,
                'new_value': old, 'old_value': new})})
        
        # Check deep
        lang = herder.model.language.Language.by_domain_id(domain_id='cc_org',
                                                           lang='en_US')
        assert lang[i18n_key].string == old

        # FIXME:
        # Re-enable this check: 
        # self.test_strings_contain(desired_key=i18n_key, desired_value=old)
        # Good, the old value is back.

        # Stop pretending to be an admin.
        logout = url_for(controller='account', action='logout')
        response = self.app.get(logout)

    def test_make_suggestion_as_non_admin(self):
        # Create a throwaway user
        u, p, n = [herder.model.user.random_alphanum() for k in range(3)]
        herder.tests.functional.test_account.do_register(self.app, 
            user_name=u, password=p, human_name=n)
        # Pretend to be that user
        self.login_as(u, p)

        # First, change it so old -> new
        i18n_key = 'country.us'
        old = 'United States'
        new = 'Untied States'
        # Just check that things are the way we thought
        self.test_strings_contain(desired_key=i18n_key, desired_value=old)

        # Now try to do the edit
        url_indeed = url_for(controller='language', action='edit_string',
            domain='cc_org', id='en_US')
        response = self.app.post(url_indeed, 
            params={'data': 
            jsonlib.write({'id': i18n_key,
                'new_value': new, 'old_value': old})})
        # And, uh, FIXME - right now we have no way of checking if it stuck

        # At least, the real string shouldn't have changed - repeat this check
        self.test_strings_contain(desired_key=i18n_key, desired_value=old)
        
        # And check that the suggestion exists in the lame UI
        url_lame = url_for(controller='language', action='lame_suggestions_ui',
            domain='cc_org', id='en_US')
        response = self.app.get(url_lame)
        assert new in response

        # Now check that we can delete it
        self.login_as('admin', admin_password)
        response = self.app.get(url_lame)
        assert new in response
