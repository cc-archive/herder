import herder.tests
from herder.tests import *

def do_register(app, user_name='bureau', password='barbecue',
                human_name = 'Mister Bureaucrat', should_fail = False):
    '''Ensure registration works'''
    url = url_for(controller='account', action='register', domain = None)
    response = app.get(url)
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
                human_name = 'Poser Bureaucrat Guy', should_fail = True)
        do_register(self.app, user_name='who_cares', password='barbecue',
                human_name = 'Disposable Man', should_fail = False)
        do_register(self.app, user_name='who_cares', password='barbecue',
                human_name = 'Poser Disposable Man', should_fail = True)

    def test_login_as_non_bureau_works(self):
        # Create a new dummy
        user_name, password, human_name = [herder.model.user.random_alphanum()
                        for i in range(3)]
        do_register(self.app, user_name=user_name, password=password, 
            human_name=human_name)
        self.login_as(user_name, password)
