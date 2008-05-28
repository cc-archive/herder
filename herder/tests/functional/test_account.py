import herder.tests
from herder.tests import *

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

    def test_can_login_as_admin(self):
        self.login_as('admin', herder.tests.admin_password)

    def test_profile_says_admin_guy(self):
        self.login_as('admin', herder.tests.admin_password)

        url = url_for(controller='account', action='profile')
        response =self.app.get(url)
        assert 'admin' in response
        assert "Admin Guy" in response

class TestAuthControllerThree(TestController):

    def do_register(self, user_name='admin', password='barbecue',
                human_name = 'Admin Guy', should_fail = False):
        '''Ensure registration works'''
        url = url_for(controller='account', action='register', domain = None)
        response = self.app.get(url)
        response.forms[0]['user_name'] = user_name
        response.forms[0]['password_once'] = password
        response.forms[0]['password_twice'] = password
        response.forms[0]['human_name'] = human_name
        response = response.forms[0].submit()
        response = response.follow() # It's a redirect, either to "OK" or "FAIL"
        if should_fail:
            assert 'has been created' not in response
        else:
            assert 'has been created' in response
        return password

    def test_registering_same_username_fails(self):
        # Assert there is already an admin user
        self.do_register(user_name='admin', password='barbecue',
                human_name = 'Admin Guy', should_fail = True)
        self.do_register(user_name='who_cares', password='barbecue',
                human_name = 'Admin Guy', should_fail = False)
        self.do_register(user_name='who_cares', password='barbecue',
                human_name = 'Admin Guy', should_fail = True)

