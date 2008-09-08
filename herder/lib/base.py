"""The base Controller API

Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""
from pylons import c, cache, config, g, request, response, session
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, etag_cache, redirect_to
from pylons.decorators import jsonify, validate
from pylons.i18n import _, ungettext, N_
from pylons.templating import render

from herder.lib.decorators import with_user_info

import herder.lib.helpers as h
import herder.model as model

class BaseController(WSGIController):
    requires_auth = ()

    def __before__(self, action):
        ''' If authentication is required, and the user is not 
        logged in, then redirect to login.'''
        if action in self.requires_auth:
            if 'user' not in session:
                # Remember where we came from so that the user can be sent there
                # after a successful login.
                session['path_before_login'] = request.path_info
                session.save()
                return redirect_to(h.url_for(controller='account', action='login'))

    ### FIXME: Don't just ignore the language ID and domain!
    def _get_roles(self, environ, domain = None, lang_id = None):
        """Return a list of roles for the current context."""
	roles = []

        user = session.get('user', None)
	if user is None:
	    return roles # empty

        # First, check for a lang_id = * role
	auths = model.meta.Session.query(model.authorization.Authorization).filter_by(user_id=user.user_id, lang_id='*').all()
	for auth in auths:
	    roles.append(model.meta.Session.query(model.role.Role).filter_by(role_id=auth.role_id).first().role_name)

        # Then check for a lang_id = lang_id role
        auths = model.meta.Session.query(model.authorization.Authorization).filter_by(user_id=user.user_id, lang_id=lang_id).all()
	for auth in auths:
	    roles.append(model.meta.Session.query(model.role.Role).filter_by(role_id=auth.role_id).first().role_name)

        # It's true that we don't check domain at all, ever.  Oh, well.

	return set(roles)

    def _actions(self, environ):
        """Return a sequence of two-tuples describing the actions for this
        view (taking into account the logged in user, roles, etc)."""

        actions = [
            ('/domain/all/list', 'Translation Domains'),
            ]

        if 'bureaucrat' in self._get_roles(environ):
            actions.append( ('/bureau', 'Bureaucracy') )

        return actions

    @with_user_info
    def __call__(self, environ, start_response):
        """Invoke the Controller"""

        # bind the actions method into the context
        c.user_roles = self._get_roles(environ)
        c.actions = self._actions(environ)

        # add actions
        if c.user:
            c.actions.insert(0, ('/account/profile', 'Your profile'))
            c.actions.append( ('/account/logout', 'Logout') )
        else:
            c.actions.append( ('/account/login', 'Login') )
            c.actions.append( ('/account/register', 'Sign up'))

        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        try:
            return WSGIController.__call__(self, environ, start_response)
        finally:
            model.meta.Session.remove()

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
