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
        
        new_user = herder.model.user.make_md5_user(user_name, herder.model.user.hash_oldskool(password), 'Your Mom')
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

            
    def test_pootle_data_import(self):
        sample_data = '''
stepmom:
  passwdhash = '982a6361e26b29f99f925742f6140752'
  name = 'Your Mom'
'''
        import jToolkit.prefs
        parser = jToolkit.prefs.PrefsParser()
        parser.parse(sample_data)
        data = parser.__root__._assignments # This *can't* be the right way...
        assert 'stepmom.passwdhash' in data

        # Groan - figure out the usernames
        user_names = set([key.split('.')[0] for key in data])

        for user_name in user_names:
            new_user = herder.model.user.make_md5_user(user_name=unicode(user_name),
                                                       human_name=unicode(data.get(user_name + '.name')),
                                                       hashed=data.get(user_name + '.passwdhash'))
            herder.model.meta.Session.save(new_user)
            herder.model.meta.Session.commit()

        
        self.login_as('stepmom', 'goodygumdrops') # goodygumdrops
                                                  # hashes to the
                                                  # above
        url = url_for(controller='account', action='profile')
        response =self.app.get(url)
        assert 'stepmom' in response
        assert "Your Mom" in response
