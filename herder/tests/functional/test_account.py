# -*- coding: utf-8 -*-
import herder.tests
import BeautifulSoup
from herder.tests import *

def do_register(app, user_name, password,
                human_name, email, should_fail = False):
    '''Ensure registration works'''
    url = url_for(controller='account', action='register', domain = None)
    response = app.get(url)
    response.forms[0]['user_name'] = user_name
    response.forms[0]['password_once'] = password
    response.forms[0]['password_twice'] = password
    response.forms[0]['human_name'] = human_name
    response.forms[0]['email'] = email
    response = response.forms[0].submit()
    response = response.follow() # It's a redirect, either to "OK" or "FAIL"
    if should_fail:
        assert 'has been created' not in response
    else:
        assert 'has been created' in response
    return password

class TestAuthControllerOne(TestController):

    def test_login_form_exists(self):
        '''Ensure the login page contains the form.'''
        login_url = url_for(controller='account', action='profile', domain = None)
        response = self.app.get(login_url) # It's a 302...
        response = response.follow()

        print response.body
        print self.app.post
        print dir(self.app)

        assert '<form action' in response.body

class TestAuthControllerTwo(TestController):

    def test_can_login_as_bureau(self):
        self.login_as('bureau', herder.tests.bureau_password)

    def test_profile_says_bureau_guy(self):
        self.login_as('bureau', herder.tests.bureau_password)

        url = url_for(controller='account', action='profile')
        response =self.app.get(url)
        assert 'bureau' in response
        assert "Mister Bureaucrat" in response

    def test_when_logged_in_login_goes_away(self):
        response = self.login_as('bureau', herder.tests.bureau_password)
        assert 'Sign up' not in response

    def test_logout(self):
        self.test_when_logged_in_login_goes_away()
        response = self.app.get(url_for(controller='account', action='logout'))
        response = response.follow()
        assert 'Sign up' in response

class TestAuthControllerThree(TestController):

    def test_registering_same_username_fails(self):
        # Assert there is already a bureau user
        do_register(self.app, user_name='bureau', password='barbecue',
                human_name = 'Poser Bureaucrat Guy', email='bureau@example.com',
                    should_fail = True)
        do_register(self.app, user_name='who_cares', password='barbecue',
                human_name = 'Disposable Man', 
                    email='who_cares@example.com', should_fail = False)
        do_register(self.app, user_name='who_cares', password='barbecue',
                human_name = 'Poser Disposable Man', 
                    email='who_cares@example.com', should_fail = True)

    def test_login_as_non_bureau_works(self):
        # Create a new dummy
        user_name, password, human_name = [herder.model.user.random_alphanum()
                        for i in range(3)]
        do_register(self.app, user_name=user_name, password=password, 
                    email=herder.model.user.random_alphanum() + '@example.com',
            human_name=human_name)
        self.login_as(user_name, password)

import herder.model.user
class TestPootleImport(TestController):
    # Pootle import story is:
    # Sometimes we get (username, md5_of_password) pairs to import
    # Upon the user successfully logging in, his password hash
    # becomes the proper salted SHA1.

    def test_create_md5_user(self):
        user_name = unicode(herder.model.user.random_alphanum())
        password = herder.model.user.random_alphanum()
        # lame: copy-pasta of user registration code
        
        new_user = herder.model.user.make_md5_user(user_name, herder.model.user.hash_oldskool(password), 'md5sucker@example.com', 'Your Mom')
        herder.model.meta.Session.save(new_user)
        herder.model.meta.Session.commit()

        # Good, now try to log in as the dude...
        self.login_as(user_name, password)

        # Good, now check that we have a salt
        db_user = herder.model.meta.Session.query(
            herder.model.user.User).filter_by(
            user_name=user_name).first()
        assert db_user.salt != 'lolwtf'
        assert len(db_user.hashed_salted_pw) != len(
            herder.model.user.hash_oldskool(password))
        assert db_user.hashed_salted_pw != \
            herder.model.user.hash_oldskool(password)

            
    sample_pootle_users_prefs = u'''
stepmom:
  passwdhash = '982a6361e26b29f99f925742f6140752'
  name = 'Ta Mère'
'''.encode('utf-8')

    def test_pootle_data_import(self):
        self.login_as('bureau', herder.tests.bureau_password)
        
        url = url_for(controller='account', action='import_pootle_users', domain=None)
        response = self.app.get(url)
        response.forms[0]['pootle_users_prefs_data'] = self.sample_pootle_users_prefs
        response = response.forms[0].submit()
        response = response.follow() # Hopefully it redirects to success
        assert 'successfully' in response
        
        # Test that it actually worked
        self.login_as('stepmom', 'goodygumdrops') # goodygumdrops
                                                  # hashes to the
                                                  # above
        url = url_for(controller='account', action='profile')
        response =self.app.get(url)
        assert 'stepmom' in response
        assert u"Ta Mère" in response

        # Test that stepmom can't do the import
        url = url_for(controller='account', action='import_pootle_users', domain=None)
        response = self.app.get(url)
        response.forms[0]['pootle_users_prefs_data'] = self.sample_pootle_users_prefs.replace('stepmom', 'evil_haxor')
        response = response.forms[0].submit()
        response = response.follow() # Who cares where it redirects to?  Can we log in?
        self.login_as('evil_haxor', 'goodygumdrops', should_fail=True)

        # Further test that stepmom can't do the import by finding the
        # form URL and posting directly
        url = url_for(controller='account',
                      action='import_pootle_users_submit', domain=None)
        response = self.app.post(url, params={'pootle_users_prefs_data':
                                       self.sample_pootle_users_prefs.replace('stepmom', 'evil_haxor')})
        self.login_as('evil_haxor', 'goodygumdrops', should_fail=True)
        
        
    def test_permissions_view_bureau_shows_up(self):
        '''Test that bureau's boxes are checked for translator and bureaucrat'''
        # Log in as admin, so we can see the page
        self.login_as('bureau', herder.tests.bureau_password)

        # Load the page
        url = url_for(controller='account', action='permissions')
        response = self.app.get(url)
        soup = BeautifulSoup.BeautifulSoup(unicode(response))

        # Check that the row about permissions includes a row about us
        bureau_row = soup(None, {'id': 'row_user_id_1'})[0]
        bureau_username = bureau_row('td')[0]
        assert bureau_username.contents[0] == 'bureau'

        # hope that thare are translator and bureaucrat boxes and that
        # they're checked for us
        inputs = bureau_row('input')
        assert len(inputs) == 2
        for input in inputs:
            assert input['checked']

    def test_permissions_change_works(self):
        '''Test that we can create a user, grant him translate rights,
        and have him actually do a translation.

        Check further that revoking those translate rights only lets him
        make suggestions.'''
        # Create a throwaway user
        u, p, e, n = [herder.model.user.random_alphanum() for k in range(4)]
        herder.tests.functional.test_account.do_register(self.app, 
                                                         user_name=u, password=p, email=e + '@example.com', human_name=n)

        ## Find the right user object
        user_obj = herder.model.meta.Session.query(herder.model.user.User).filter_by(
            user_name=u).first()

        # Grant translator permission
        all_translator = herder.model.authorization.Authorization()
        all_translator.user_id = user_obj.user_id
        all_translator.lang_id = '*'
        all_translator.domain_id = '*'
        all_translator.role_id = herder.model.meta.Session.query(herder.model.role.Role).filter_by(
            role_name='translator').first().role_id
        herder.model.meta.Session.save(all_translator)
        herder.model.meta.Session.commit()
        
        # log in as the guy
        self.login_as(u, p)

        # have him edit
        gensym = herder.model.user.random_alphanum()
        tlc = herder.tests.functional.test_language.TestLanguageController()
        tlc.app = self.app
        tlc.test_edit_string_as_bureau(skip_login_step=True)

        # Log in as admin, so we can see the permissions page
        self.login_as('bureau', herder.tests.bureau_password)
        
        # Grab the permissions page
        url = url_for(controller='account', action='permissions')
        response = self.app.get(url)

        checkbox_prefix = 'user_n_role_%d_' % user_obj.user_id
      
        assert response.forms[0][checkbox_prefix + '1'].checked == False
        assert response.forms[0][checkbox_prefix + '2'].checked == True
        response.forms[0][checkbox_prefix + '2'].checked = False
        response = response.forms[0].submit()
        response = response.follow() # it's a redirect back to this page

        # verify that the boxes are gone, because the user is gone
        # from the list of people with authorizations
        assert (checkbox_prefix + '1') not in response.forms[0].fields
        assert (checkbox_prefix + '2') not in response.forms[0].fields

        self.login_as(u,p)

        # Verify that he can (only) submit suggestions
        tlc = herder.tests.functional.test_language.TestLanguageController()
        tlc.app = self.app
        tlc.test_make_suggestion_as_non_bureau(skip_login_step=True)
        tlc.test_delete_suggestion()


        
