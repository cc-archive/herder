import logging

from herder.lib.base import *
import herder.model.user
import sqlalchemy.exceptions

log = logging.getLogger(__name__)

class AccountController(BaseController):
    requires_auth = ['profile']

    def login(self):
        return render('/account/login.html')

    def login_submit(self):
        '''Verify username and password.'''
        # Both fields filled?
        form_username = unicode(request.params.get('username'))
        form_password = unicode(request.params.get('password'))
        if form_password is None:
            no_password_submitted
        if form_username is None:
            no_username_submitted
        
        # Get user data from database
        db_user = herder.model.meta.Session.query(herder.model.user.User).filter_by(user_name=form_username).first()

        if db_user is None:
            # FIXME: Be a redirect
            no_such_user
            return redirect_to(h.url_for(action='login', reason='No such user.'))
        
        # Check the password.
        if herder.model.user.hash_with_salt(raw_password=form_password,
                          salt=db_user.salt) != db_user.hashed_salted_pw:
            # FIXME: Be a redirect
            bad_pass
            return redirect_to(h.url_for(action='login', reason='Incorrect password submitted'))

        # Great - this is for real.
        session['user'] = db_user
        session.save()

        if 'path_before_login' in session:
            go_here = session['path_before_login']
            del session['path_before_login']
            redirect_to(go_here)
        else: # Nowhere to go, say hi
            return redirect_to(h.url_for(action='login_successful'))

    def login_successful(self):
        return render('/account/login_successful.html')

    def register(self):

        return render('/account/registration/index.html')

    def register_success(self):
        return render('/account/registration/success.html')

    def register_failed(self):
        return render('/account/registration/failed.html')

    def register_submit(self):
        success = False
        reason = ''

        # First, check password1 == password2
        if request.params['password_once'] == request.params['password_twice']:
            # Great, try to create the user now.
            new_user = herder.model.user.User()
            new_user.user_name = unicode(request.params['user_name'])
            new_user.salt = herder.model.user.random_alphanum()
            new_user.hashed_salted_pw = herder.model.user.hash_with_salt(
                            salt=new_user.salt,
                            raw_password=request.params['password_once'])
            new_user.human_name = request.params['human_name']
            herder.model.meta.Session.save(new_user)

            try:
                herder.model.meta.Session.commit()
                success = True
            except sqlalchemy.exceptions.IntegrityError, e:
                success = False
                if 'column user_name is not unique' in e.message:
                    reason = 'A user by this name already exists.'
                    herder.model.meta.Session.rollback()
                else:
                    raise # I don't know why the exception was thrown
                          # so I can't handle it.

	    # Grant no authorizations by default, unless the username is bureau.
	    # In that case, grant some nice blanket permissions.

	    if success and new_user.user_name == 'bureau':

		# bureau for *, and
		new_bureau_auth = herder.model.authorization.Authorization()
		new_bureau_auth.user_id = new_user.user_id
		new_bureau_auth.lang_id = '*'
		new_bureau_auth.domain_id = '*'
		new_bureau_auth.role_id = herder.model.meta.Session.query(herder.model.role.Role).filter_by(role_name='bureaucrat').first().role_id
		herder.model.meta.Session.save(new_bureau_auth)

		# translate for *
		new_translate_auth = herder.model.authorization.Authorization()
		new_translate_auth.user_id = new_user.user_id
		new_translate_auth.lang_id = '*'
		new_translate_auth.domain_id = '*'
		new_translate_auth.role_id = herder.model.meta.Session.query(herder.model.role.Role).filter_by(role_name='translate').first().role_id
		herder.model.meta.Session.save(new_translate_auth)
		
		herder.model.meta.Session.commit()
		# Just hope it worked; it really should not fail,
		# and I have no real way to handle the failure.
		# (should I delete the bureau user if it does fail? Geez.)

            # Great!
	else:
            success = False
            reason = "The two passwords you submitted do not match."

        if success:
            redirect_to(action='register_success')
        else:
            redirect_to(action='register_failed')

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
        return redirect_to(h.url_for(action='logged_out'))

    def logged_out(self):
        return render('/account/logged_out.html')
