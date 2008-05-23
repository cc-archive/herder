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

    def test_login_override(self, username = 'admin'):
        '''Ensure we can appear to be logged in (since we need this for
        other tests.)'''
        # claim to be admin
        self.app.extra_environ['REMOTE_USER'] = 'admin'
        # Go somewhere we expect to be asked to log in
        login_url = url_for(controller='account', action='profile', domain = None)
        response = self.app.get(login_url)

        assert len(response.forms) == 0
        del self.app.extra_environ['REMOTE_USER']
    
class TestAuthControllerThree(TestController):

    def test_can_register(self):
        '''Ensure registration works'''
        url = url_for(controller='account', action='register', domain = None)
        response = self.app.get(url)
        response.forms[0]['username'] = 'admin'
        response.forms[0]['password_once'] = 'barbecue'
        response.forms[0]['password_twice'] = 'barbecue'
        response.forms[0]['human_name'] = 'Admin Guy'
        response.forms[0].submit()
    
        

