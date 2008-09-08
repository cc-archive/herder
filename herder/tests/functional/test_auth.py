# -*- coding: utf-8 -*-
import herder.tests
from herder.tests import *
import herder.tests.functional.test_account
import herder.tests.functional.test_language

class TestAuthBackend(TestController):

    def test_translate_auth_star(self):
        '''Test that granting someone the * translate power lets him
        actually edit strings.'''
        # Create a user
        u, p, e, h = [herder.model.user.random_alphanum() for i in range(4)]
        u = __name__ + '_' + u
        herder.tests.functional.test_account.do_register(self.app,
                                              user_name=u,
                                              password=p,
                                              email=e + '@example.com',
                                              human_name=h)
        # Authorize him to edit star
        ## Find the right user object
        user_obj = herder.model.meta.Session.query(herder.model.user.User).filter_by(
            user_name=u).first()

        # Create the all translator object
        all_translator = herder.model.authorization.Authorization()
        all_translator.user_id = user_obj.user_id
        all_translator.lang_id = '*'
        all_translator.domain_id = '*'
        all_translator.role_id = herder.model.meta.Session.query(herder.model.role.Role).filter_by(
            role_name='translator').first().role_id
        herder.model.meta.Session.save(all_translator)
        herder.model.meta.Session.commit()

        # Log in as that sucker
        self.login_as(u, p)

        # Make sure the login worked
        assert u in self.app.get(url_for(controller='account',
                                         action='profile'))
        
        # have him edit
        gensym = herder.model.user.random_alphanum()
        tlc = herder.tests.functional.test_language.TestLanguageController()
        tlc.app = self.app
        tlc.test_edit_string_as_bureau(skip_login_step=True)
        
