import logging

from herder.lib.base import *
import herder.model.user
import sqlalchemy.exceptions
import collections

log = logging.getLogger(__name__)

def bless_user(bless_you):
    # bureau for *, and
    new_bureau_auth = herder.model.authorization.Authorization()
    new_bureau_auth.user_id = bless_you.user_id
    new_bureau_auth.lang_id = u'*'
    new_bureau_auth.domain_id = u'*'
    new_bureau_auth.role_id = herder.model.meta.Session.query(herder.model.role.Role).filter_by(role_name=u'bureaucrat').first().role_id
    herder.model.meta.Session.save(new_bureau_auth)
    
    # translator for *
    new_translator_auth = herder.model.authorization.Authorization()
    new_translator_auth.user_id = bless_you.user_id
    new_translator_auth.lang_id = u'*'
    new_translator_auth.domain_id = u'*'
    new_translator_auth.role_id = herder.model.meta.Session.query(herder.model.role.Role).filter_by(role_name=u'translator').first().role_id
    herder.model.meta.Session.save(new_translator_auth)
    
    herder.model.meta.Session.commit()
    # Just hope it worked; it really should not fail,
    # and I have no real way to handle the failure.
    # (should I delete the bureau user if it does fail? Geez.)

class AccountController(BaseController):
    requires_auth = ['profile', 'change_password',
                     'change_password_submit',
                     'profile_submit',
                     ]

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
                          salt=db_user.salt) == db_user.hashed_salted_pw:
            pass # keep on truckin'!
        # We could be storing an old-style password.
        elif herder.model.user.hash_oldskool(form_password) == \
                db_user.hashed_salted_pw:
            herder.model.user.upgrade_password(db_user, form_password)
            herder.model.meta.Session.commit()
            # success
        else:
            # FIXME: Be a redirect
            bad_pass
            return redirect_to(h.url_for(action='login', reason='Incorrect password submitted'))

        # Great - this is for real.
        session['_user_id'] = db_user.user_id
        session['user'] = db_user # FIXME: One day this should get out of 
                                  # the session since it is truly transient.
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

        assert request.params['email']
        assert '@' in request.params['email']

        # First, check password1 == password2
        if request.params['password_once'] == request.params['password_twice']:
            # Great, try to create the user now.
            new_user = herder.model.user.User()
            new_user.user_name = unicode(request.params['user_name'])
            new_user.salt = herder.model.user.random_alphanum()
            new_user.hashed_salted_pw = herder.model.user.hash_with_salt(
                            salt=new_user.salt,
                            raw_password=request.params['password_once'])
            new_user.human_name = unicode(request.params['human_name'])
            new_user.email = unicode(request.params['email'])
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
        lang_id = '*'
        domain_id = '*'
        prefs_keys = [ pref.pref_name for pref in herder.model.meta.Session.query(
                herder.model.pref.Pref).filter_by(
                user_id=session['_user_id'], lang_id=lang_id, domain_id=domain_id)]
        prefs_data = dict( [
                (key, herder.model.pref.get_pref(user_id=session['_user_id'],
                                                 lang_id=lang_id, domain_id=domain_id, pref_name=key).pref_value ) for key in prefs_keys])

        # show what we are opted-in to get email notifications for
        email_notify_list = [ pref.lang_id for pref in
                              herder.model.meta.Session.query(
                herder.model.pref.Pref).filter_by(
                user_id=session['_user_id'], domain_id=domain_id, pref_name='email_notify', pref_value=True)]

        # provide a list of all languages
        all_languages = set()
        for domain in herder.model.domain.Domain.all():
             all_languages.update(map(unicode,domain.languages))

        return render('/account/profile.html', prefs_data=prefs_data,
                      email_notify_list=email_notify_list, all_languages=sorted(all_languages))

    def logout(self):
        '''Log the user out and display a confirmation message'''
        if 'user' in session:
            del session['user']
            del session['_user_id']
            session.save()
        return redirect_to(h.url_for(action='logged_out'))

    def logged_out(self):
        return render('/account/logged_out.html')

    def import_pootle_users(self):
        '''Show a simple text box asking for the Pootle users file.'''
        return render('/account/import_pootle_users.html')

    def import_pootle_users_submit(self):
        '''Create new users based on the Pootle users.prefs file.'''
        # First, check that we have the * bureaucrat privilege
        if 'bureaucrat' not in self._get_roles(request.environ):
            return redirect_to(h.url_for(action='login', 
                                         reason='You tried to do something that requires being a bureaucrat.  Would you like to log in as one?'))
        
        # We must be okay at this point.
        pootle_users_prefs = request.params['pootle_users_prefs_data']
        pootle_users_prefs_as_utf8 = pootle_users_prefs.encode('utf-8')
        import jToolkit.prefs
        parser = jToolkit.prefs.PrefsParser()
        parser.parse(pootle_users_prefs_as_utf8)
        data = parser.__root__._assignments # This *can't* be the right way...
        
        # Groan - figure out the usernames
        user_names = set([key.split('.')[0] for key in data])
        
        for user_name in user_names:
            new_user = herder.model.user.make_md5_user(user_name=unicode(user_name),
                                                       human_name=unicode(data.get(user_name + '.name'), 'utf-8'),
                                                       email=unicode(data.get(user_name + '.email', ''), 'utf-8'),
                                                       hashed=data.get(user_name + '.passwdhash'))
            herder.model.meta.Session.save(new_user)
            herder.model.meta.Session.commit()

        # That seemed to go okay.
        return redirect_to(h.url_for(action='import_pootle_users_successful'))

    def import_pootle_users_successful(self):
        '''Tell the user the import went okay, but frustratingly
        provide no information on what users got imported.'''
        return render('/account/import_pootle_users_successful.html')

    def permissions(self):
        '''Show what permissions different users have, and let people
        change them.'''
        # Oh my GOD, this code sucks.  I'm sorry.
        general_role_info = herder.model.meta.Session.query(herder.model.role.Role).all()
        all_languages_list = []
        [all_languages_list.extend(domain.languages) for domain in herder.model.domain.Domain.all()]
        all_languages = set(all_languages_list)

        auth_data = herder.model.meta.Session.query(herder.model.authorization.Authorization).all()

        roles_data = {}
        for auth in auth_data:
            if auth.lang_id not in roles_data:
                roles_data[auth.lang_id] = {}

            if auth.user_id not in roles_data[auth.lang_id]:
                roles_data[auth.lang_id][auth.user_id] = {}
            me = roles_data[auth.lang_id][auth.user_id]

            # Make sure me has a username
            if 'username' not in me:
                assert 'user_id' not in me
                me['user_id'] = auth.user_id

                user = herder.model.meta.Session.query(
                    herder.model.user.User).filter_by(
                    user_id=auth.user_id).one()
                user_name = user.user_name
                me['username'] = user_name

            # Add this authorization to me
            if 'role_names' not in me:
                me['role_names'] = set()
                assert 'role_ids' not in me
                me['role_ids'] = set()
            my_role_names = me['role_names']

            role = herder.model.meta.Session.query(
                herder.model.role.Role).filter_by(role_id=auth.role_id).one()
            role_name = role.role_name
            my_role_names.add(role_name)

            me['role_ids'].add(auth.role_id)

        all_users = herder.model.meta.Session.query(
            herder.model.user.User)

        return render('/account/permissions.html',
                      roles_data=roles_data,
                      general_role_info=general_role_info,
                      all_languages=all_languages,
                      all_users = all_users)


    def permissions_submit(self):
        '''Verify username and password.'''
        # Both fields filled?
        form_username = unicode(request.params.get('username'))
        form_password = unicode(request.params.get('password'))
        import collections
        user2role = collections.defaultdict(lambda:
                                                collections.defaultdict(set))

        # First, parse out the non-add requests
        for key in request.params.keys():
            if key.startswith('user_n_role_'):
                if request.params[key].lower() == 'on':
                    user, role, lang = key.replace('user_n_role_','').split('_', 2)
                    user, role = map(int, (user, role))
                    user2role[user][lang].add(role)
            else:
                if 'new_role_user_id' in request.params:
                    user = int(request.params['new_role_user_id'])
                    lang_id = request.params['new_role_lang_id']
                    roles = set()
                    # OMG N^2, wtf.
                    for key in request.params:
                        if key.startswith('new_role_'):
                            if request.params[key].lower() == 'on':
                                role_num = int(key.replace('new_role_', ''))
                                user2role[user][lang_id].add(role_num)

        # Time to mass-set the authorization table
        domain_id = '*' # LOL, this controller sucks
        # Need to gather the list of user_ids with current assignments
        # plus the ones we've been POSTed about

        # First, grab the list of user_ids from both the POSTed data
        # and the list of authorizations in the database.
        user_ids = user2role.keys()
        user_ids.extend(
            [c.user_id for c in 
             model.meta.Session.query(model.authorization.Authorization).all()])
        user_ids = set(map(int, user_ids))

        # Then, grab all the languages.
        all_languages_list = ['*']
        [all_languages_list.extend(domain.languages) for domain in herder.model.domain.Domain.all()]
        all_languages = set(map(unicode, all_languages_list))

        for user_id in user_ids:
            for lang_id in all_languages:
                # for each user ID we know about
                # look up its language entry and see what was POSTed there.
                role_ids_from_POST = user2role[user_id][lang_id]

                # Grab all the existing authorizations for this user ID
                db_auth_objs = model.meta.Session.query(model.authorization.Authorization).filter_by(user_id=user_id, lang_id=lang_id).all()
                role_ids_from_DB = set([a.role_id for a in db_auth_objs])
                
                role_ids_to_add = set()
                role_ids_to_remove = set()
                # For every role ID assigned in the DB, check if it was POSTed.
                # If it was not POSTed, then remove it later.
                for role_id_from_DB in role_ids_from_DB:
                    if role_id_from_DB not in role_ids_from_POST:
                        role_ids_to_remove.add(role_id_from_DB)

                # For every role ID that was POSTed, if it is not in the DB,
                # mark it to be added.
                for role_id_from_POST in role_ids_from_POST:
                    if role_id_from_POST not in role_ids_from_DB:
                        role_ids_to_add.add(role_id_from_POST)

                # Great, now act on that.
                for db_auth_obj in db_auth_objs:
                    if db_auth_obj.role_id in role_ids_to_remove:
                        assert 'bureaucrat' in self._get_roles(request.environ,
                                                               lang_id=lang_id)
                        herder.model.meta.Session.delete(db_auth_obj)

                for role_id_to_add in role_ids_to_add:
                    # Create the new auth that corresponds to that
                    new_auth = herder.model.authorization.Authorization()
                    new_auth.user_id = user_id
                    new_auth.lang_id = lang_id
                    new_auth.domain_id = domain_id
                    new_auth.role_id = role_id_to_add
                    assert 'bureaucrat' in self._get_roles(request.environ,
                                                           lang_id=lang_id)
                    herder.model.meta.Session.save(new_auth)

        # Wait until the end to commit.
        herder.model.meta.Session.commit()

        return redirect_to(h.url_for(action='permissions'))

    def change_password(self):
        return render('/account/change_password.html')

    def change_password_submit(self):
        form_password = unicode(request.params.get('old_password'))
        # Zeroth, check if the user's password matches
        if herder.model.user.hash_with_salt(raw_password=form_password,
                                            salt=session['user'].salt) != \
                                            session['user'].hashed_salted_pw:
            redirect_to(action='change_password', reason='Bad password given.')

        # First, check password1 == password2
        if request.params['password_once'] == request.params['password_twice']:
            # Great, set the dude's password to that.
            session['user'].salt = herder.model.user.random_alphanum()
            session['user'].hashed_salted_pw = herder.model.user.hash_with_salt(
                salt=session['user'].salt,
                raw_password=request.params['password_once'])
            herder.model.meta.Session.commit()
            redirect_to(action='profile', message='Password successfully changed.')
        else:
            redirect_to(action='change_password_failed', reason = "The two passwords you submitted do not match.")

    def profile_submit(self):
        user_id = session['_user_id']
        lang_id = '*'
        domain_id = '*'

        # First, handle lang-independent boolean preferences
        key2value = collections.defaultdict(bool)
        for key in request.params.keys():
            if key.startswith('pref_'):
                if request.params[key].lower() == 'on':
                    key2value[key.split('pref_', 1)[1]] = True

        # The false ones usually don't get submitted, so we have to
        # figure out their names from the DB.
        keys = key2value.keys()
        keys.extend( [
                pref.pref_name for pref in herder.model.meta.Session.query(
                    herder.model.pref.Pref).filter_by(
                    user_id=user_id, lang_id=lang_id, domain_id=domain_id)])

        for key in set(keys):
            herder.model.pref.set_pref(user_id=user_id, lang_id=lang_id,
                                       domain_id=domain_id, pref_name=key,
                                       pref_value=key2value[key])

        # Then, handle lang-dependent boolean preferences
        key2langs = collections.defaultdict(set)
        for by_lang_key in filter(lambda k: k.startswith('by_lang_'),
                                  request.params):
            short_key = by_lang_key.split('by_lang_pref_', 1)[1]
            key2langs[short_key].update(
                request.params.getall(by_lang_key))

        # need to pull keys from DB, lamesauce
        for pref in herder.model.meta.Session.query(
            herder.model.pref.Pref):
            if pref.lang_id != '*': # FIXME: Move this to the SELECT
                if pref.pref_name not in key2langs:
                    key2langs[pref.pref_name] = set()

        # To make things false, we actually remove the pref from the DB
        for key in key2langs:
            these_should_be_true = key2langs[key]
            # This gives us the set of languages that are true,
            # we need to query the prefs table to see what languages
            # are set to True that should be cleared.
            these_were_in_db = [ pref.lang_id for pref in 
                                 herder.model.meta.Session.query(
                    herder.model.pref.Pref).filter_by(
                    pref_name=key, user_id=session['_user_id'], domain_id='*')]

            # First, go through what's in the DB and set what should
            # be true to true.  If we have any remaining lang_ids in
            # these_should_be_true, we set them to true at the end.

            # The performance of this isn't great.

            for lang_id in these_were_in_db:
                if lang_id in these_should_be_true:
                    herder.model.pref.set_pref(
                        user_id=session['_user_id'], lang_id=lang_id,
                        domain_id='*', pref_name=key, pref_value=True)
                    these_should_be_true.remove(lang_id)
                else:
                    herder.model.pref.set_pref(
                        user_id=session['_user_id'], lang_id=lang_id,
                        domain_id='*', pref_name=key, pref_value=False)
            
            # Finally, set the remaining ones to True
            for lang_id in these_should_be_true:
                herder.model.pref.set_pref(
                    user_id=session['_user_id'], lang_id=lang_id,
                    domain_id='*', pref_name=key, pref_value=True)

        herder.model.meta.Session.commit()
        redirect_to(action='profile')
