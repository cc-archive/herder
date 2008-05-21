from herder.tests import *
import herder.model

class TestLoginController(TestController):
    
    def test_login_form_exists(self):
        '''Ensure the login page contains the form.'''
        login_url = url_for(controller='login', action='login', domain = None)
        response = self.app.get(login_url)

        print response.body
        print self.app.post
        print dir(self.app)

        assert '<form action' in response.body

    def test_login_override(self, username = 'admin'):
        '''Ensure we can appear to be logged in (since we need this for
        other tests.)'''
        # claim to be admin
        self.app.extra_environ['REMOTE_USER'] = 'admin'
        login_url = url_for(controller='login', action='login', domain = None)
        response = self.app.get(login_url)

        assert len(response.forms) == 0
        
