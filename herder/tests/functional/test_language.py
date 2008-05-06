from herder.tests import *
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
        return True # FIXME: Test something here someday
       
    def test_edit_string_as_admin(self):
        # Pretend to be admin
        self.app.extra_environ['REMOTE_USER'] = 'admin'
        # First, change it so old -> new
        # Then, change it back (just because I feel bad)
        old = 'United States'
        new = 'Untied States'
        url_indeed = url_for(controller='language', action='edit_string',
            domain='cc_org', id='en_US')
        response = self.app.post(url_indeed, 
            params={'data': 
            jsonlib.write({'data': {'id': 'country.us', 
                'new_value': new, 'old_value': old}})})
        del self.app.extra_environ['REMOTE_USER']
        
