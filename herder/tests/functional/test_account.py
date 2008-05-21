from herder.tests import *

class TestAuthController(TestController):

    def test_login_override(self):
        """Ensure we can appear to be logged in (since we need this
        for other tests)."""

        # claim to be admin
        self.app.extra_environ['REMOTE_USER'] = 'admin'

        login_url = url_for(controller='account', action='login')
        response = self.app.get(login_url)

        # make sure the form isn't there
        assert len(response.forms) == 0
