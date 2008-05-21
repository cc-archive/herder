import logging

from herder.lib.base import *
import herder.model.user

log = logging.getLogger(__name__)

class AccountController(BaseController):
    requires_auth = ['profile']

    def login(self):
        return render('/account/login.html')

    def submit(self):
        '''Verify username and password.'''
        # Both fields filled?
        form_username = unicode(request.params.get('username'))
        form_password = unicode(request.params.get('password'))
        
        # Get user data from database
        print herder.model.meta.Session
        fail
        #db_user = herder.model.user.query(herder.model.).get_by(form_username)
        if db_user is None:
            return render('/account/login.html', reason='No such user.')
        
        # Check the password.
        if hash_with_salt(raw_password=form_password,
                          salt=db_user.salt) != db_user.hashed_salted_pw:
            return render('/account/login.html', reason='Incorrect password submitted')

        # Great - this is for real.
        session['user'] = form_username
        session.save()

        if 'path_before_login' in session:
            go_here = session['path_before_login']
            del session['path_before_login']
            redirect_to(go_here)
        else: # Nowhere to go, say hi
            return render('/account/loggedin.html')

    def register(self):

        return render('/account/registration/index.html')

    def confirm(self):

        # get the hash from the query string
        # reg_hash = ...

        # check the registration
        registration = model.UserRegistration.exists(reg_hash)
        if registration:

            # registration valid
            model.users.user_create(registration.username, 
                                    password=registration.password, 
                                    group="Users")

            return render('/account/registration/success.html')

        else:
            return render('/account/registration/invalid.html')

    def profile(self):
        return render('/account/profile.html')

    def logout(self):
        '''Log the user out and display a confirmation message'''
        if 'user' in session:
            del session['user']
            session.save()
        return render('/account/logout.html')
