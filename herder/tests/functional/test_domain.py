from herder.tests import *

class TestDomainController(TestController):

    def test_index(self):
        # FIXME: Going to just /domain should return a list of domains
        #response = self.app.get(url_for(controller='domain'))
        pass

    def test_list(self):
        response = self.app.get(url_for(controller='domain', action='view', id='cc_org'))
        assert '.git' not in response.body
        assert 'fr_CA' in response.body
        assert 'mk' in response.body

    # FIXME: Figure out other tests...
